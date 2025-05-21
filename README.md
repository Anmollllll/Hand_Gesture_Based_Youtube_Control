# Hand_Gesture_Based_Youtube_Control

This project is a computer vision-based project that enables you to control YouTube playback using simple hand gestures. With the help of MediaPipe, OpenCV, and PyAutoGUI, it transforms your hand into a virtual remote to adjust volume, control playback, seek forward/backward, and even change playback speed—all without touching your keyboard.

---

## 🖥️ Features

 Gesture-based control using your webcam  
 Adjust system volume by thumb and index finger and set with pinky finger (Left hand)  
 Seek forward with left thumb and backward with right thumb in YouTube videos   
 Play/Pause the video all fingers except thumb.  (Right hand gesture)
 Speed up with index finger and slow down with pinky finger (Right hand gestures)  
 Hand stabilization logic for accurate detection  
 Gesture cooldown to prevent repeated inputs

---

## 📂 Project Structure

```bash
.
├── main.py               # Main script for webcam and gesture capture
├── gesture_fnc.py        # Core logic for interpreting hand gestures
