## Insect Image Cropper Desktop Application

This repository contains 3 applications for insects image cropping, built using PyQt, allows users to load and crop insect images using three different methods. 

1. Load image: Users can select and display insect images from a provided folder.

2. Crop insect: Users can crop insects from images using one of the three approaches:

*manualcrop: user can crop the image by manually drawing a bounding box around insect

*imageprocessing: image can be automatically cropped by applying classical image processing method

*objectdetection: image can be cropped by applying a pretrained object detection model

project_root/

│── Images/                 # Folder containing original insect images
│── cropped_images/          # Repository where cropped images are saved
│   │── manualcropped/               # Results from manual cropping
│   │── imageprocessing/     # Results from classical image processing
│   │── objectdetection/     # Results from object detection model
│── manualcrop.py             # Script for manual cropping
│── imageprocessing.py        # Script for classical image processing
│── objectdetection.py        # Script for object detection-based cropping
│── README.md                 # Project documentation

## Dependencies

Please make sure that you have Python 3 installed with all the required dependencies:

*PyQt5

*Numpy

*Opencv-python

*Pillow

*Torch       # required for object detection

*torchvision 

## Installation

0. Open Windows Command Line

1. Create a new folder for the project at your desired path and navigate to it in CMD:
    '''

    mkdir <path/to/image_crop_application>

    cd <path/to/image_crop_application>

    '''

2. Clone the repository to your local machine:

    '''

    git clone https://gitlab.kit.edu/uyugr/insects.git 

    '''

   To sychronize your local repository with the remote, you can run:

    '''

    git fetch origin

    '''

3. Install the required dependencies 

4. Start the application:

    '''

    python <filename.py>

    '''


## Usage

1. There are 3 buttons at the bottom of the application, click the button "Load Image" to choose one image which needs to be cropped.

2. *manualcrop: After loading image, click the button "manual crop", and thenuser can draw a bounding box on the image.

    *imageprocessing: After loading image, click the button "crop insect", the image can be cropped automatically.
   
    *objectdetection: After loading image, click the button "detect and crop Insect", the image can be cropped automatically. (When use this method, user needs always adjust the size of application interface)

3. click the button ""save crop", the cropped result can be saved in the folder you choose.

## Further Enhancement

*Apply other pre-trained object detection models.

*Improve accuracy of classical image processing techniques.