import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class InsectCropperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insect Cropper App")
        self.setGeometry(100, 100, 800, 600)


        #Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        #Image display label
        self.image_label = QLabel("Load an image to get started")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        #Buttons
        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.crop_button = QPushButton("Crop Insect")
        self.crop_save_button = QPushButton("Save Crop")
        self.crop_button.setEnabled(False)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.crop_button)
        self.button_layout.addWidget(self.crop_save_button)
        self.layout.addLayout(self.button_layout)

        
        

        #Button actions
        self.load_button.clicked.connect(self.load_image)
        self.crop_button.clicked.connect(self.crop_insect)
        self.crop_save_button.clicked.connect(self.save_cropped_image)

        #Attributes for image handling
        self.image_path = None
        self.cv_image = None

    def load_image(self):
        #Open file dialog to select an image
        options = QFileDialog.Options()
        #you can change the filepath
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "D:/insects/Images/", "Images (*.png *.jpg *.jpeg *.bmp)", options=options
        )

        if file_path:
            self.image_path = file_path
            self.cv_image = cv2.imread(file_path)
            self.display_image(self.cv_image)
            self.crop_button.setEnabled(True)

    def crop_insect(self):
        if self.cv_image is not None:
            #Convert to grayimage
            gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)

            #Apply thresholding to create a binary mask
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
           
            #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            edges = cv2.Canny(thresh, threshold1=100, threshold2=200)
            kernel = np.ones((3,3), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=2)  #dilation
            eroded = cv2.erode(dilated, kernel, iterations=1)  #erosion

            #Find contours
            contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            #Get the largest contour (assumes the insect is the largest object)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                #rect = (rect_center, (width, height), angle)
                rect = cv2.minAreaRect(largest_contour)

                #get 4 points of the rect
                box = cv2.boxPoints(rect)
                box = np.int32(box)  

                x, y, w, h = cv2.boundingRect(box)

                #Crop the region of interest
                self.cropped_image = self.cv_image[y:y+h, x:x+w]

                #Display cropped image
                self.display_image(self.cropped_image)

    def display_image(self, image):
        #get the size of QLabel
        label_width = self.image_label.width()
        label_height = self.image_label.height()

        #get the size of original image
        original_height, original_width, _ = image.shape

        #scale
        self.scale_factor_w = label_width / original_width
        self.scale_factor_h = label_height / original_height
        new_width = int(original_width * self.scale_factor_w)
        new_height = int(original_height * self.scale_factor_h)

        #resize image
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        #convert to Qt format
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        #display
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

    def save_cropped_image(self):
        """save cropped image"""
        if self.cropped_image is None:
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Cropped Image", "D:/insects/cropped_images/classicalprocessing/", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            cv2.imwrite(file_path, self.cropped_image)
            print(f"Cropped image saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InsectCropperApp()
    window.show()
    sys.exit(app.exec_())
