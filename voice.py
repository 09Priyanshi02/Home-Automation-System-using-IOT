import speech_recognition as sr
import serial
import time
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()
arduino_port = 'COM4'
arduino = serial.Serial(arduino_port, 9600)
time.sleep(2)

def turn_led_on():
    arduino.write(b'1')

def turn_led_off():
    arduino.write(b'0')

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
        print(f"Could not request results; {e}")

def smoke_detected():
    print("Smoke detected! Please evacuate the room immediately.")
    speak("Smoke detected! Please evacuate the room immediately.")
    print("move to exit 2")
    speak("move to exit 2")

while True:
    if arduino.readline().decode('ascii').strip() == "smoke":
        smoke_detected()
        listen_for_commands()
