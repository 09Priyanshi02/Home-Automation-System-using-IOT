import speech_recognition as sr
import serial
import time
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import cv2

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Define the COM port for Arduino
arduino_port = 'COM4'  # Change this to your Arduino's port

# Establish serial communication with Arduino
arduino = serial.Serial(arduino_port, 9600)
time.sleep(2)  # Wait for Arduino to initialize

def turn_led_on():
    arduino.write(b'1')  # Send '1' to turn the LED on

def turn_led_off():
    arduino.write(b'0')  # Send '0' to turn the LED off

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

# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True, help="Path to MobileNetSSD prototxt file")
ap.add_argument("-m", "--model", required=True, help="Path to MobileNetSSD model file")
ap.add_argument("-c", "--confidence", type=float, default=0.2, help="Minimum probability to filter weak detections")
ap.add_argument("-v", "--video", type=str, default="", help="Path to input video file")
args = vars(ap.parse_args())

# Initialize the list of class labels MobileNet SSD was trained to detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
           "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
           "tvmonitor"]

# Generate a set of bounding box colors for each class
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load the serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# Initialize the video stream, allow the camera sensor to warm up, and initialize the FPS counter
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()  # Change src=0 to your camera index if needed
time.sleep(2.0)
fps = FPS().start()

# Main loop to continuously listen for commands and process video frames
while True:
    listen_for_commands()
    
    # Grab the frame from the threaded video stream and resize it to have a maximum width of 800 pixels
    frame = vs.read()
    if frame is None:
        break
    frame = imutils.resize(frame, width=800)
    
    # Grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

    # Pass the blob through the network and obtain the detections and predictions
    net.setInput(blob)
    detections = net.forward()

    # Loop over the detections
    num_people = 0
    for i in np.arange(0, detections.shape[2]):
        # Extract the confidence (i.e., probability) associated with the prediction
        confidence = detections[0, 0, i, 2]
        
        # Filter out weak detections by ensuring the confidence is greater than the minimum confidence
        if confidence > args["confidence"]:
            # Extract the index of the class label from the detections
            idx = int(detections[0, 0, i, 1])

            # Increment the count of people detected
            if CLASSES[idx] == "person":
                num_people += 1

            # Compute the (x, y)-coordinates of the bounding box for the object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # Draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    # Print the number of people detected
    print("Number of people in the room:", num_people)

    # Send command to Arduino based on number of people detected
    if num_people > 0:
        arduino.write(b'1')  # Send command to turn light on
    else:
        arduino.write(b'0')  # Send command to turn light off

    # Show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the 'q' key was pressed, break from the loop
    if key == ord("q"):
        break

    # Update the FPS counter
    fps.update()

# Stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# Clean up
cv2.destroyAllWindows()
vs.stop()
