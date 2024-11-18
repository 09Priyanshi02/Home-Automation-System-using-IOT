import speech_recognition as sr
import serial
import time
import pyttsx3

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Define the COM port for Arduino
arduino_port = 'COM4'  # Change this to your Arduino's port

# Establish serial communication with Arduino
arduino = serial.Serial(arduino_port, 9600)
time.sleep(2)  # Wait for Arduino to initialize

def turn_led_on():
    arduino.write(b'1')  # Send '1' to turn the LED on

def turn_led_off():
    arduino.write(b'0')  # Send '0' to turn the LED off

def speak(text):
    engine.say(text)
    engine.runAndWait()

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

# Function to handle smoke detection alert
def smoke_detected():
    print("Smoke detected! Please evacuate the room immediately.")
    speak("Smoke detected! Please evacuate the room immediately.")
    print("move to exit 2")
    speak("move to exit 2")

# Main loop to continuously listen for commands and handle smoke detection alerts
while True:
    # Check if smoke is detected from Arduino
    if arduino.readline().decode('ascii').strip() == "smoke":
        smoke_detected()
        # Trigger voice command to alert user
        listen_for_commands()
