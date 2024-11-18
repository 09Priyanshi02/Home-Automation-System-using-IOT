import speech_recognition as sr
import serial
import time
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import cv2

recognizer = sr.Recognizer()
arduino_port = 'COM4'
arduino = serial.Serial(arduino_port, 9600)
time.sleep(2)

def turn_led_on():
    arduino.write(b'1')

def turn_led_off():
    arduino.write(b'0')

def listen_for_commands():
    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print("You said:", command)
        if "turn on" in command:
            turn_led_on()
        elif "turn off" in command:
            turn_led_off()
        else:
            print("Command not recognized.")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True, help="Path to MobileNetSSD prototxt file")
ap.add_argument("-m", "--model", required=True, help="Path to MobileNetSSD model file")
ap.add_argument("-c", "--confidence", type=float, default=0.2, help="Minimum probability to filter weak detections")
ap.add_argument("-v", "--video", type=str, default="", help="Path to input video file")
args = vars(ap.parse_args())

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
           "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
           "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

while True:
    listen_for_commands()
    frame = vs.read()
    if frame is None:
        break
    frame = imutils.resize(frame, width=800)
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    num_people = 0
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > args["confidence"]:
            idx = int(detections[0, 0, i, 1])
            if CLASSES[idx] == "person":
                num_people += 1
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
    print("Number of people in the room:", num_people)
    if num_people > 0:
        arduino.write(b'1')
    else:
        arduino.write(b'0')
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    fps.update()

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()
