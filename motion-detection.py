import cv2
import numpy as np
import time
import pygame
from datetime import datetime
import os
import sys
import tkinter as tk
from tkinter import messagebox, Scale, Button, Label, Frame
from PIL import Image, ImageTk
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class MotionDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motion Detection System")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create frames
        self.control_frame = Frame(root)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.video_frame = Frame(root)
        self.video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        Label(self.control_frame, text="Sensitivity:").grid(row=0, column=0, padx=5, pady=5)
        self.sensitivity = Scale(self.control_frame, from_=100, to=1000, orient=tk.HORIZONTAL, length=200)
        self.sensitivity.set(500)
        self.sensitivity.grid(row=0, column=1, padx=5, pady=5)
        
        self.start_button = Button(self.control_frame, text="Start Detection", command=self.start_detection)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_button = Button(self.control_frame, text="Stop Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.record_button = Button(self.control_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Status display
        self.status_label = Label(self.control_frame, text="Status: Not Running", fg="red")
        self.status_label.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        # Video display
        self.video_label = Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Motion detection variables
        self.cap = None
        self.running = False
        self.detection_thread = None
        self.record = False
        self.out = None
        self.recording_path = None
        
        # Initialize pygame for audio
        pygame.init()
        pygame.mixer.init()
        
        # Load the alert sound
        try:
            if getattr(sys, 'frozen', False):
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            sound_path = os.path.join(application_path, "alert.wav")
            self.alert_sound = pygame.mixer.Sound(sound_path)
        except (pygame.error, FileNotFoundError):
            messagebox.showwarning("Warning", f"Could not load sound file. Make sure 'alert.wav' exists at {sound_path}")
            self.alert_sound = None
        
        # Add these to your control_frame setup
        Label(self.control_frame, text="Min Area:").grid(row=2, column=0, padx=5, pady=5)
        self.min_area = Scale(self.control_frame, from_=100, to=2000, orient=tk.HORIZONTAL, length=200)
        self.min_area.set(500)
        self.min_area.grid(row=2, column=1, padx=5, pady=5)

        Label(self.control_frame, text="Threshold:").grid(row=2, column=2, padx=5, pady=5)
        self.threshold_value = Scale(self.control_frame, from_=50, to=250, orient=tk.HORIZONTAL, length=200)
        self.threshold_value.set(200)
        self.threshold_value.grid(row=2, column=3, padx=5, pady=5)
        
        # Add these new variables
        self.email_notifications = False
        self.email_cooldown = 60  # seconds between emails
        self.last_email_time = 0
        
        # Add a button to your control frame
        self.email_button = Button(self.control_frame, text="Enable Email Alerts", command=self.toggle_email)
        self.email_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    
    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera.")
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Running", fg="green")
        
        self.detection_thread = threading.Thread(target=self.motion_detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def stop_detection(self):
        if self.record:
            self.toggle_recording()  # Stop recording if it's active
        
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg="red")
        self.video_label.config(image=None)
        self.video_label.image = None
    
    def motion_detection_loop(self):
        backSub = cv2.createBackgroundSubtractorMOG2(history=self.sensitivity.get(), varThreshold=25, detectShadows=True)
        last_alert_time = time.time() - 10  # Allow immediate first alert
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to grab frame.")
                self.stop_detection()
                break
            
            # Apply the background subtractor
            fgMask = backSub.apply(frame)
            
            # Clean up the mask with blur and thresholding
            fgMask = cv2.GaussianBlur(fgMask, (5, 5), 0)
            thresh = cv2.threshold(fgMask, self.threshold_value.get(), 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Find contours on the threshold image
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            current_motion = False
            for contour in contours:
                if cv2.contourArea(contour) < self.min_area.get():  # Use the slider value
                    continue
                current_motion = True
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Display status and timestamp
            status_text = "Status: {}".format("Motion Detected" if current_motion else "No Motion")
            cv2.putText(frame, status_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            
            # Play alert sound if motion detected and cooldown period passed
            if current_motion and time.time() - last_alert_time > 3:
                print("Motion detected at", datetime.now().strftime("%I:%M:%S%p"))
                if self.alert_sound:
                    self.alert_sound.play()
                last_alert_time = time.time()
                
                # Send email alert
                self.send_email_alert(frame)
            
            # Update the GUI with the current frame
            self.update_frame(frame)
            
            # Short delay to reduce CPU usage
            time.sleep(0.03)
            
            if self.record and self.out:
                self.out.write(frame)
    
    def update_frame(self, frame):
        # Convert the frame to a format Tkinter can display
        cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_image)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        
        # Update the label
        self.video_label.config(image=tk_image)
        self.video_label.image = tk_image  # Keep a reference to prevent garbage collection
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.stop_detection()
            pygame.quit()
            self.root.destroy()
    
    def toggle_recording(self):
        if not self.record:
            # Start recording
            if not self.cap or not self.running:
                messagebox.showwarning("Warning", "Start detection first before recording.")
                return
            
            # Create output directory if it doesn't exist
            if getattr(sys, 'frozen', False):
                recordings_dir = os.path.join(os.path.dirname(sys.executable), "recordings")
            else:
                recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
            
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Create a filename with current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.recording_path = os.path.join(recordings_dir, f"motion_{timestamp}.avi")
            
            # Get video properties
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 20.0
            
            # Create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(self.recording_path, fourcc, fps, (frame_width, frame_height))
            
            self.record = True
            self.record_button.config(text="Stop Recording", bg="red")
            self.status_label.config(text="Status: Recording", fg="red")
        else:
            # Stop recording
            if self.out:
                self.out.release()
                self.out = None
            
            self.record = False
            self.record_button.config(text="Start Recording", bg="SystemButtonFace")
            self.status_label.config(text="Status: Running", fg="green")
            messagebox.showinfo("Recording Saved", f"Video saved to {self.recording_path}")
    
    def toggle_email(self):
        if not self.email_notifications:
            # Configure email settings
            self.email_config = {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'your_email@gmail.com',  # User should configure this
                'password': 'your_app_password',     # User should configure this
                'recipient': 'recipient@example.com' # User should configure this
            }
            
            self.email_notifications = True
            self.email_button.config(text="Disable Email Alerts", bg="orange")
        else:
            self.email_notifications = False
            self.email_button.config(text="Enable Email Alerts", bg="SystemButtonFace")
    
    def send_email_alert(self, frame):
        if not self.email_notifications:
            return
        
        current_time = time.time()
        if current_time - self.last_email_time < self.email_cooldown:
            return
        
        self.last_email_time = current_time
        
        try:
            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = self.email_config['recipient']
            msg['Subject'] = f"Motion Detected - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add text
            text = MIMEText(f"Motion was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            msg.attach(text)
            
            # Add the image
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()
            image = MIMEImage(img_bytes)
            image.add_header('Content-Disposition', 'attachment', filename='motion.jpg')
            msg.attach(image)
            
            # Send the email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email alert sent at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Failed to send email: {e}")

def main():
    root = tk.Tk()
    app = MotionDetectionApp(root)
    root.geometry("800x600")
    root.mainloop()

if __name__ == "__main__":
    main()
