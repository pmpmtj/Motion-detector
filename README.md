# Motion Detection System

A Python-based motion detection application that uses computer vision to detect and record movement through a webcam feed. The application provides real-time monitoring with customizable sensitivity, email alerts, and video recording capabilities.

![Motion Detection System](https://via.placeholder.com/800x450.png?text=Motion+Detection+System)

## Features

- **Real-time Motion Detection**: Uses OpenCV's background subtraction to identify movement in the camera feed
- **Customizable Sensitivity**: Adjust detection parameters including sensitivity, threshold, and minimum area
- **Visual Indicators**: Highlights detected motion with green bounding boxes
- **Video Recording**: Record footage when motion is detected
- **Alert System**: Audio alerts when motion is detected
- **Email Notifications**: Receive email alerts with snapshot images when motion is detected
- **User-friendly Interface**: Simple Tkinter GUI for easy control and monitoring

## Requirements

- Python 3.6+
- OpenCV
- NumPy
- Pygame
- Pillow (PIL)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/motion-detection-system.git
   cd motion-detection-system
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Add an audio file named `alert.wav` to the project directory for sound alerts

## Usage

1. Run the application:
   ```
   python motion-detection.py
   ```

2. Configure the application:
   - Adjust the sensitivity slider to control how sensitive the motion detection is
   - Set the minimum area to filter out small movements
   - Adjust the threshold value to fine-tune detection

3. Click "Start Detection" to begin monitoring
4. Optional features:
   - Click "Start Recording" to save video footage
   - Enable email alerts by clicking "Enable Email Alerts" (requires configuration)

## Email Configuration

To use the email alert feature, you need to configure your email credentials in the code:

1. Open `motion-detection.py`
2. Find the `toggle_email` method
3. Update the following fields with your information:
   ```python
   self.email_config = {
       'enabled': True,
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587,
       'username': 'your_email@gmail.com',  # Your email address
       'password': 'your_app_password',     # Your app password
       'recipient': 'recipient@example.com' # Recipient email address
   }
   ```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password. See [Google's documentation](https://support.google.com/accounts/answer/185833) for more information.

## Customization

- **Alert Sound**: Replace `alert.wav` with your preferred sound file
- **Recording Location**: Recordings are saved in a `recordings` folder in the application directory
- **Email Cooldown**: Adjust the `email_cooldown` variable to change the minimum time between email alerts

## Acknowledgments

- Special thanks to the Cursor.ai team for their innovative AI-assisted development tools that helped in creating and refining this project
- This project builds upon the incredible work of the OpenCV community and their contributions to computer vision
- Thanks to the broader open source community for creating and maintaining the libraries that make this project possible, including NumPy, Pygame, and Pillow
- Appreciation to all developers who share their knowledge through documentation, tutorials, and forum discussions, making projects like this accessible to everyone

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 