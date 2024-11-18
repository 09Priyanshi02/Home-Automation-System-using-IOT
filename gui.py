import serial
import tkinter as tk

smoke_detected = False  # Flag to track if smoke has been detected
led_status = False       # Variable to store LED status

def receive_data():
    global smoke_detected
    while True:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                # Print received data
                print("Received data:", data)
                # Append received data to the Tkinter text widget
                # text.insert(tk.END, data + '\n')
                text.see(tk.END)
                # Check if smoke is detected
                if "Smoke detected" in data and not smoke_detected:
                    print("Smoke detected!")
                    # Set the flag to True to indicate smoke has been detected
                    smoke_detected = True
                    # Provide an alert message
                    alert_msg = "Alert: Smoke detected! Move out of the room!"
                    print(alert_msg)
                    text.insert(tk.END, alert_msg + '\n')
                    text.see(tk.END)
                    # Add LED toggle button after smoke detection
                    toggle_button.pack()
                    # Exit the loop after smoke detection
                    break
        except UnicodeDecodeError:
            print("Error decoding data from serial port")

def toggle_led():
    global led_status
    # Toggle LED status
    led_status = not led_status
    # Send command to Arduino based on LED status
    command = "1" if led_status else "0"
    ser.write(command.encode())

ser = serial.Serial('COM4', 9600)  # Replace 'COMX' with your Arduino's serial port

root = tk.Tk()
root.title("Arduino Data Receiver")

text = tk.Text(root)
text.pack()

# Create LED toggle button (initially hidden)
toggle_button = tk.Button(root, text="Toggle LED", command=toggle_led)

# Start a thread to continuously receive data from Arduino
import threading
thread = threading.Thread(target=receive_data)
thread.daemon = True
thread.start()

root.mainloop()

# After the main loop exits (window closed by user), close the serial connection
ser.close()
