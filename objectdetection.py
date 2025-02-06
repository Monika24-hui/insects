import sys
import cv2
import torch
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")

    def set_image(self, image):
        """Display image on QLabel"""
        height, width, channel = image.shape
        bytes_per_line = channel * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setScaledContents(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insect Detection and Cropping")
        self.setGeometry(100, 100, 800, 600)

        #Buttons
        self.image_label = ImageLabel(self)
        self.load_button = QPushButton("Load Image")
        self.detect_button = QPushButton("Detect and Crop Insect")
        self.save_button = QPushButton("Save Crop")

        #Connections
        self.load_button.clicked.connect(self.load_image)
        self.detect_button.clicked.connect(self.detect_and_crop)
        self.save_button.clicked.connect(self.save_crop)

        self.detect_button.setEnabled(False)
        self.save_button.setEnabled(False)

        #Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.save_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        #Initialize attributes
        self.original_image = None
        self.cropped_image = None

        #Load the object detection model
        self.model = self.load_model()

    def load_model(self):
        """Load a pre-trained YOLO model"""
        print("Loading model...")
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', 'custom', force_reload=True)
        print("Model loaded successfully.")
        return model

    def load_image(self):
        """Load an image"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options)

        if file_path:
            self.original_image = cv2.imread(file_path)
            rgb_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.image_label.set_image(rgb_image)
            self.detect_button.setEnabled(True)
            self.filename = os.path.basename(file_path)
            print("Selected file name:", self.filename)

    def detect_and_crop(self):
        """Detect insects and crop the detected region"""
        if self.original_image is None:
            return

        print("Detecting insects...")
        results = self.model(self.original_image)
        detections = results.xyxy[0].numpy()  #Extract bounding boxes

        if len(detections) > 0:
            x1, y1, x2, y2, conf, cls = detections[0]
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

            #Crop the detected region
            self.cropped_image = self.original_image[y1:y2, x1:x2]
            rgb_cropped = cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2RGB)
            self.image_label.set_image(rgb_cropped)
            self.save_button.setEnabled(True)
            print("Insect is detected and cropped")
        else:
            print("No insects detected")

    def save_crop(self):
        """Save the cropped image"""
        if self.cropped_image is None:
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Cropped Image", self.filename, "Images (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            cv2.imwrite(file_path, self.cropped_image)
            print(f"Cropped image saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
