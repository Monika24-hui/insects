import sys
import cv2
import numpy as np
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.is_cropping = False
        self.image = None  #store current image

    def paintEvent(self, event):
        """show the bounding box when user crop the image manually"""
        super().paintEvent(event)  
        
        if self.is_cropping and self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            width = abs(self.end_point.x() - self.start_point.x())
            height = abs(self.end_point.y() - self.start_point.y())
            painter.drawRect(x, y, width, height)

    def set_image(self, image):
        self.image = image
        self.update_pixmap(self.image)

    def update_pixmap(self, image):
        """display the image and adjust the size"""

        #get the size of QLabel
        label_width = self.width()
        label_height = self.height()

        #get the size of original image
        original_height, original_width, _ = image.shape
        self.scale_x = original_width / label_width
        self.scale_y = original_height / label_height
        #adjust the size
        resized_image = cv2.resize(image, (label_width, label_height), interpolation=cv2.INTER_AREA)


        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)  #convert image to rgb format
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width  #calculate the number of bytes per line(row)
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)  #convert into Qpixmap object, which is required for displaying on a QLabel
        self.setPixmap(pixmap)
        self.setScaledContents(True)

    
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.setWindowTitle("Insects Crop")
        self.setGeometry(100, 100, 800, 600)
        #self.setGeometry(200, 200, 1600, 1200)

        #Widgets
        self.image_label = ImageLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black")

        load_button =  QPushButton("Load Image")
        manual_crop_button = QPushButton("manual crop")
        save_crop_button = QPushButton("save crop")

        load_button.clicked.connect(self.load_image)
        manual_crop_button.clicked.connect(self.enable_manual_crop)
        save_crop_button.clicked.connect(self.save_crop)

        #Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(load_button)
        button_layout.addWidget(manual_crop_button)
        button_layout.addWidget(save_crop_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(button_layout)
        bottom = QLabel("Do not chnage the size of the app after loading image")
        bottom.setFixedHeight(30)
        main_layout.addWidget(bottom)

        container = QWidget()
        container.setLayout(main_layout)                                                                          
        self.setCentralWidget(container)

    def load_image(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "open iamge file", "", "Images(*.png *.jpg *.bmp)", options=options)
        if filepath:
            self.image = cv2.imread(filepath)
            self.image_label.set_image(self.image)
            self.filename = os.path.basename(filepath)
            print("Selected file name:", self.filename)

    def enable_manual_crop(self):
        if self.image_label.image is None:
            return
        self.image_label.is_cropping = True
        self.image_label.start_point = None
        self.image_label.end_point = None
    
    def mousePressEvent(self, event):
        """capture the event: press the mouse"""
        if self.image_label.is_cropping and event.button() == Qt.LeftButton:
            #convert the position of mouse to position on QLabel
            self.image_label.start_point = self.image_label.mapFromParent(event.pos())

    def mouseMoveEvent(self, event):
        """capture the event: move the mouse"""
        if self.image_label.is_cropping and self.image_label.start_point:
            #position update
            self.image_label.end_point = self.image_label.mapFromParent(event.pos())
            self.image_label.update()

    def mouseReleaseEvent(self, event):
        """capture the event: release the mouse"""
        if self.image_label.is_cropping and event.button() == Qt.LeftButton:
            self.image_label.end_point = self.image_label.mapFromParent(event.pos())
            self.image_label.update()
            self.crop_manual()

    def crop_manual(self):
        if self.image_label.start_point and self.image_label.end_point and self.image_label.image is not None:
            #calculate bouding box
            x1 = min(self.image_label.start_point.x(), self.image_label.end_point.x())
            y1 = min(self.image_label.start_point.y(), self.image_label.end_point.y())
            x2 = max(self.image_label.start_point.x(), self.image_label.end_point.x())
            y2 = max(self.image_label.start_point.y(), self.image_label.end_point.y())

            #convert to the position on original image
            x1_original = int(x1 * self.image_label.scale_x)
            y1_original = int(y1 * self.image_label.scale_y)
            x2_original = int(x2 * self.image_label.scale_x)
            y2_original = int(y2 * self.image_label.scale_y)


            self.cropped_image = self.image_label.image[y1_original:y2_original, x1_original:x2_original]
            self.image_label.set_image(self.cropped_image)
            self.image_label.is_cropping  = False

    def save_crop(self):
        if self.cropped_image is None:
            return
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(self, "save crop", self.filename, "Images(*.png *.jpg *.jpeg *.bmp)", options=options)
        if filepath:
            cv2.imwrite(filepath, self.cropped_image)
            print(f"cropped image is saved to{filepath}")
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MyWindow()
    main_window.show()
    sys.exit(app.exec_())
