# File Extension Converter Web App

## Overview
This is a Python-based Flask web application that allows users to upload files and convert their extensions to a desired format. The application ensures secure file handling and provides a user-friendly interface.

## Features
- Upload any supported file type.
- Select the target extension from a dropdown menu.
- Convert the file extension and download the renamed file directly from the browser.

##Installation
-pip install flask

##Usage
index file should be in templates folder which is exist in same directory with app.py
upload folder created automatically if didn't exist(inside it uploaded file will be saved)

Start the Flask development server:
run python app.py

Open your browser and go to http://127.0.0.1:5000/.
Click on the "Choose File" button to select a file.
Select the desired extension from the dropdown menu (e.g., txt, png, pdf).
Click "Convert" to rename the file and download it.

project/
│
├── app.py                   # Main Flask application file
├── uploads/                 # Directory for uploaded files
└── templates/
    └── index.html           # HTML template for the homepage