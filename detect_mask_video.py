# USAGE
# python detect_mask_video.py

# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import FPS
from pi_video import VideoGetAndShow
import numpy as np
import argparse
import time
import cv2
import os
import socket
import RPi.GPIO as GPIO  

flag = 0

GPIO.setmode(GPIO.BCM)  
  
# GPIO 23 set up as input. It is pulled up to stop false signals  

GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def detect_and_predict_mask(frame, faceNet, maskNet):
    start = time.time()
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

    end = time.time()
    print(f"Runtime of the detect and mask prediction is {end - start} seconds")

    # return a 2-tuple of the face locations and their corresponding
    # locations
    return (locs, preds)

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
ap.add_argument("-n", "--num-frames", type=int, default=100,
    help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
    help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

print("[INFO] loading face detector model...")
prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
weightsPath = os.path.sep.join([args["face"],
    "res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)


# # load the face mask detector model from disk
print("[INFO] loading face mask detector model...")
maskNet = load_model(args["model"])

# Initialize necessary variables
i = 0
rpi_data = []
maskcount = 0
nomaskcount = 0

# Connect to the Arduino
# Replace host and port with host and port of RPi
host = '192.168.1.219'
port = 5008

s = socket.socket()
s.bind((host,port))

print('Binded to ' + str(host) + ' ' + str(port))
s.listen(1)
client, addr = s.accept()
print("Connection from: " + str(addr))

# created a *threaded *video stream, allow the camera sensor to warmup,
print("[INFO] sampling THREADED frames from `picamera` module...")
video_getter_and_shower = VideoGetAndShow().start()

try:
    while True:
        # loop over the frames from the video stream
        if video_getter_and_shower.stopped:
            video_getter_and_shower.stop()
            break

        if GPIO.input(23) == GPIO.LOW:
            print("Button pushed!")
            flag = 1
            # Start the FPS counter
            fps = FPS().start()
            time.sleep(1)

        while flag:
            frame = video_getter_and_shower.getFrame()

            # update the FPS counter
            fps.update()

            allMask = True
            numfaces = []

            if i == 2:
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
                    cv2.imshow("Video", frame)

                if allMask == True:
                    rpi_data.append(1)
                    maskcount = maskcount + 1
                else:
                    rpi_data.append(0)
                    nomaskcount = nomaskcount + 1
                i = 0

            i = i + 1

            if len(rpi_data) == 3:
                print(rpi_data) #included this to make sure logic works

                # stop the timer and display FPS information
                fps.stop()
                print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
                if maskcount > nomaskcount:
                    print("Mask detected")
                    client.send("MASK".encode('utf-8'))
                else:
                    print("No Mask detected")
                    client.send("NO MASK".encode('utf-8'))
                maskcount = 0
                nomaskcount = 0
                rpi_data.clear()
                flag = 0
                break
except KeyboardInterrupt:
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    client.close()
