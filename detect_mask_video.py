# USAGE
# python detect_mask_video.py

# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import socket

from picamera.array import PiRGBArray
from picamera import PiCamera

import RPi.GPIO as GPIO  

flag = -1

GPIO.setmode(GPIO.BCM)  
  
# GPIO 23 set up as input. It is pulled up to stop false signals  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
   
# now the program will do nothing until the signal on port 23   
# starts to fall towards zero. This is why we used the pullup  
# to keep the signal high and prevent a false interrupt   

def my_callback(channel):
    flag = 1

GPIO.add_event_detect(23, GPIO.RISING, callback=my_callback) 

def detect_and_predict_mask(frame, faceNet, maskNet):
    # grab the dimensions of the frame and then construct a blob
    # from it
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
        (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the face detections
    faceNet.setInput(blob)
    detections = faceNet.forward()

    # initialize our list of faces, their corresponding locations,
    # and the list of predictions from our face mask network
    faces = []
    locs = []
    preds = []

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the detection
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the confidence is
        # greater than the minimum confidence
        if confidence > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # ensure the bounding boxes fall within the dimensions of
            # the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # extract the face ROI, convert it from BGR to RGB channel
            # ordering, resize it to 224x224, and preprocess it
            face = frame[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)

            # add the face and bounding boxes to their respective
            # lists
            faces.append(face)
            locs.append((startX, startY, endX, endY))

    # only make a predictions if at least one face was detected
    if len(faces) > 0:
        # for faster inference we'll make batch predictions on *all*
        # faces at the same time rather than one-by-one predictions
        # in the above `for` loop
        faces = np.array(faces, dtype="float32")
        preds = maskNet.predict(faces, batch_size=32)

    # return a 2-tuple of the face locations and their corresponding
    # locations
    return (locs, preds)

# def send_data(data):
#     # Replace host and port with host and port of RPi
#     host = '192.168.1.101'
#     port = 5000

#     s = socket.socket()
#     s.bind((host,port))

#     print('Binded to ' + str(host) + ' ' + str(port))
#     s.listen(1)
#     c, addr = s.accept()
#     print("Connection from: " + str(addr))
#     while True:
#         # data = c.recv(1024).decode('utf-8')
#         # if not data:
#         #     break
#         # print("From connected user: " + data)
#         # data = data.upper()
#         # print("Sending: " + data)
#         c.send(data.encode('utf-8'))
#     c.close()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--face", type=str,
    default="face_detector",
    help="path to face detector model directory")
ap.add_argument("-m", "--model", type=str,
    default="mask_detector.model",
    help="path to trained face mask detector model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized face detector model from disk
print("[INFO] loading face detector model...")
prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
weightsPath = os.path.sep.join([args["face"],
    "res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load the face mask detector model from disk
print("[INFO] loading face mask detector model...")
maskNet = load_model(args["model"])





####################################### NEW
i = 0
rpi_data = []
maskcount = 0
nomaskcount = 0

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
            # vs = VideoStream(src=0).start()
            # time.sleep(2.0)
print("interrupt detected")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera)
time.sleep(2.0)
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            #frame = vs.read()


while True:
    # loop over the frames from the video stream
 
    while flag:
           
        camera.capture(rawCapture, format="bgr")
        frame = rawCapture.array
        
        frame = imutils.resize(frame, width=400)

        #################################### NEW
        allMask = True
        numfaces = []

        # detect faces in the frame and determine if they are wearing a
        # face mask or not
        (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)

        # loop over the detected face locations and their corresponding
        # locations
        for (box, pred) in zip(locs, preds):
            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            # determine the class label and color we'll use to draw
            # the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

            ######################### NEW
            if label == "No Mask":
                allMask = False
                

            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output
            # frame
            cv2.putText(frame, label, (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        ####################################### NEW

        if i == 2:
            if allMask == True:
                rpi_data.append(1)
                maskcount = maskcount + 1
            else:
                rpi_data.append(0)
                nomaskcount = nomaskcount + 1
            i = 0

        i = i+1

        if len(rpi_data) == 10:
            print(rpi_data) #included this to make sure logic works
            if maskcount > nomaskcount:
                print("Mask")
                # send_data("Mask")
            else:
                print("No Mask")
                # send_data("No Mask")
            maskcount = 0
            nomaskcount = 0
            rpi_data.clear()
            flag = 0
            

        ##########################################

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
            
        rawCapture.truncate(0)


# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
