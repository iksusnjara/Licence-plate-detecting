# Licence-plate-detecting
Algorithms for detecting licence plates on car images. Created for Internet of Things course in Algebra College University masters in data science. Task was to develop algorithm able to read characters from a licence plate of a vehicle approaching parking barrier. Final version of code manages to do so with over 80% accuracy.

Project is fully developed in Python 3, using OpenCV library for image processing and PyTesseract OCR. 

First step is licence plate detection on an image of approaching car. As the car approaches parking barrier, it triggers a sensor which takes a photo of a car. This photo is then processed using OpenCV, where algorithms for edge detection are employed. After that, white rectangle template is matched to find position of a licence plate in car image. Finally, only licence plate is cropped.

Next step is reading characters from licence plate using PyTesseract OCR. Before applying Tesseract function, licence plate image is further processed, using OpenCV filters and thresholding.

This repository contains python scripts, notebooks and other files from many intermediate steps. Final python code used is lp_reader.py, which contains LP reading function written as a Python class. Its usage is demonstrated in MAIN class notebook. Also, code in these files is well commented and documented.
