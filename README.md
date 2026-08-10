<div align="center">

# 🖐️

# 0xAirCanvas

### Write in the air.
### Create without touching the screen.

Built with **Python + Flask + OpenCV + MediaPipe**

<br/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00E5FF?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Computer Vision](https://img.shields.io/badge/Computer%20Vision-Real--Time-A855F7?style=for-the-badge)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-34D399?style=for-the-badge)](LICENSE)

<br/>

**Created by Abhishek Jadhav**
**[@0xAbhi13](https://github.com/0xAbhi13)**

</div>

---

## ⚡ What is 0xAirCanvas?

0xAirCanvas turns your webcam into a pen. Raise your index finger, move it
through the air, and watch your hand's fingertip become a smooth, glowing
stroke on a live digital canvas — no stylus, no touchscreen, no mouse.

Under the hood, a Flask backend runs OpenCV + MediaPipe hand tracking on
every camera frame, classifies your hand into one of four gestures, and
streams the resulting drawing events straight into a browser `<canvas>` in
real time.

```text
> Initializing 0xAirCanvas...
> Camera connected ✓
> MediaPipe initialized ✓
> Hand detected ✓
> Gesture engine online ✓
> AirCanvas ready.
```

---

## 🎥 Demo

<div align="center">

`assets/demo.gif`

*(placeholder — record a real demo after running the app locally; see*
*`assets/README.md` *for instructions. No fabricated media is included.)*

</div>

## 📸 Preview

<div align="center">

`assets/preview.png`

*(placeholder — add a real screenshot of the running app; see*
*`assets/README.md`.)*

</div>

---

## ✨ Features

<table>
<tr>
<td width="33%">

### 🖐️ Real-Time Hand Tracking
21-point hand landmark detection powered by MediaPipe, running live on
every frame.

</td>
<td width="33%">

### ✍️ Air Writing
Your index fingertip becomes a digital pen — smoothed, low-jitter strokes
rendered directly onto the canvas.

</td>
<td width="33%">

### 🎨 Custom Brushes
Adjustable brush size with a glowing, neon-style stroke.

</td>
</tr>
<tr>
<td width="33%">

### 🌈 Multiple Colors
Seven-color palette, switch instantly mid-drawing.

</td>
<td width="33%">

### 🧹 Smart Eraser
Adjustable eraser size with the same smoothing pipeline as the brush.

</td>
<td width="33%">

### ↩️ Undo / Redo
Full history stack — step backward and forward through every stroke.

</td>
</tr>
<tr>
<td width="33%">

### 💾 PNG Export
Save your artwork as a PNG with one click or a keyboard shortcut.

</td>
<td width="33%">

### 📊 Live System HUD
Camera status, hand detection, current gesture, and FPS — always visible.

</td>
<td width="33%">

### ✨ Futuristic UI
Glassmorphism, neon glow, animated HUD elements, a genuinely premium feel.

</td>
</tr>
</table>

<div align="center">

### 🔒 Local Camera Processing

All video processing happens on your machine. Nothing is uploaded or stored.

</div>

---

## 🕹️ Gesture Guide

| Gesture | Action |
|---|---|
| ☝️ Index Finger | Draw |
| ✋ Open Palm | Stop |
| ✊ Fist (held briefly) | Clear |
| 🤏 Pinch | Interact (toggle brush / eraser) |

Gestures are debounced — a fist has to be held for a fraction of a second
before the canvas clears, so a single noisy frame can't wipe your drawing.

---

## 🧠 How It Works

```text
📷 Webcam
      ↓
🧠 MediaPipe          — detects 21 hand landmarks per frame
      ↓
🖐️ Hand Landmarks     — pixel + normalized coordinates for every joint
      ↓
☝️ Fingertip Tracking — isolates the index fingertip, classifies the gesture
      ↓
📍 Coordinate Smoothing — exponential moving average removes jitter
      ↓
✍️ Drawing Engine      — turns smoothed points into start/move/end stroke events
      ↓
🎨 Digital Artwork     — the browser renders strokes live on an HTML canvas
```

The camera frame is streamed to the browser as MJPEG (`/video_feed`), and
stroke/status events are pushed over Server-Sent Events (`/api/events`) —
so the drawing itself is rendered by the browser's Canvas API, staying
smooth and independent of video frame rate.

---

## 🧰 Tech Stack

🐍 Python · 🌐 Flask · 👁️ OpenCV · 🖐️ MediaPipe · 🔢 NumPy
🎨 HTML5 Canvas · ⚡ Vanilla JavaScript · 🎨 CSS3

---

## 📦 Installation

```bash
git clone https://github.com/0xAbhi13/0xAirCanvas.git
cd 0xAirCanvas

python -m venv venv
```

**Windows activation:**

```bash
venv\Scripts\activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Run:**

```bash
python app.py
```

Then open the local Flask URL shown in your terminal (typically
`http://127.0.0.1:5000`).

> Replace the clone URL above with your own repository once you've pushed
> this project to GitHub.

---

## ▶️ Usage

1. Launch the app and allow camera access when prompted by your browser/OS.
2. Raise your index finger in view of the camera to start drawing.
3. Open your palm to stop drawing without erasing anything.
4. Hold a fist briefly to clear the canvas.
5. Pinch your thumb and index finger together to toggle between brush and
   eraser.
6. Use the control panel (or keyboard shortcuts) to change brush size,
   color, undo/redo, or save your artwork as a PNG.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `B` | Brush |
| `E` | Eraser |
| `C` | Clear |
| `Z` | Undo |
| `Y` | Redo |
| `S` | Save |
| `H` | Help |
| `Esc` | Close modal |

---

## 🗂️ Project Structure

```text
0xAirCanvas/
│
├── app.py                     # Flask app, camera loop, streaming routes
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── vision/
│   ├── __init__.py
│   ├── hand_tracker.py        # MediaPipe Hands wrapper
│   ├── gesture_detector.py    # Gesture classification + debounce
│   └── drawing_engine.py      # Smoothing + stroke event generation
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── assets/
│       ├── logo.svg
│       └── favicon.svg
│
└── assets/
    ├── demo.gif                # add after recording locally
    ├── screenshot.png          # add after recording locally
    └── preview.png             # add after recording locally
```

---

## 🔒 Privacy

🔒 Camera processing happens locally. Your video is not uploaded or stored.
0xAirCanvas makes no network calls with your video data — everything runs
inside your own Flask server and browser.

---

## 🛣️ Future Roadmap

- [ ] Multi-hand drawing
- [ ] Air handwriting recognition
- [ ] Shape recognition
- [ ] AI-assisted drawing
- [ ] Gesture-based shortcuts
- [ ] Drawing replay
- [ ] Advanced brush effects
- [ ] Image import

---

## 👨‍💻 Author

# Abhishek Jadhav

Creator of 0xAirCanvas.

Building creative projects with Python, AI, computer vision, and web
technologies.

GitHub: [@0xAbhi13](https://github.com/0xAbhi13)

---

## 📄 License

Released under the [MIT License](LICENSE).

<div align="center">

Made with ☝️ and a webcam.

</div>
