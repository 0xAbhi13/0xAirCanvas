<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00E5FF,100:A855F7&height=220&section=header&text=0xAirCanvas&fontSize=70&fontColor=ffffff&fontAlignY=38&desc=Write%20in%20the%20air.%20Create%20without%20touching%20the%20screen.&descAlignY=58&descSize=18&animation=fadeIn" width="100%"/>

<br/>

<a href="https://github.com/0xAbhi13/0xAirCanvas">
  <img src="https://readme-typing-svg.demolab.com/?lines=%E2%98%9D%EF%B8%8F+Raise+your+finger...;%E2%9C%8D%EF%B8%8F+The+webcam+becomes+a+pen...;%F0%9F%8E%A8+Draw+in+mid-air...;%E2%9C%A8+No+stylus.+No+mouse.+No+touch.;%F0%9F%9A%80+Just+you%2C+your+hand%2C+and+a+camera.&font=JetBrains%20Mono&center=true&width=680&height=45&duration=2600&pause=900&color=00E5FF&vCenter=true&size=22" alt="Typing SVG" />
</a>

<br/><br/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00E5FF?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-34D399?style=for-the-badge)](LICENSE)

![Stars](https://img.shields.io/github/stars/0xAbhi13/0xAirCanvas?style=for-the-badge&color=fbbf24&logo=github)
![Forks](https://img.shields.io/github/forks/0xAbhi13/0xAirCanvas?style=for-the-badge&color=f472b6&logo=github)
![Last Commit](https://img.shields.io/github/last-commit/0xAbhi13/0xAirCanvas?style=for-the-badge&color=a855f7)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-34D399?style=for-the-badge)

<br/>

**Created by Abhishek Jadhav — [@0xAbhi13](https://github.com/0xAbhi13)**

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.gif" width="100%">

<div align="center">

### 📚 Table of Contents

[⚡ About](#-what-is-0xaircanvas) • [✨ Features](#-features) • [🕹️ Gestures](#️-gesture-guide) • [🧠 How It Works](#-how-it-works) • [📦 Install](#-installation) • [▶️ Usage](#️-usage) • [⌨️ Shortcuts](#️-keyboard-shortcuts) • [🗂️ Structure](#️-project-structure) • [🛣️ Roadmap](#️-future-roadmap) • [📄 License](#-license)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.gif" width="100%">

## ⚡ What is 0xAirCanvas?

**0xAirCanvas** turns your webcam into a pen. Raise your index finger, move it through the air, and watch your fingertip become a smooth, glowing stroke on a live digital canvas — no stylus, no touchscreen, no mouse.

Under the hood, a Flask backend runs OpenCV + MediaPipe hand tracking on every camera frame, classifies your hand into one of four gestures, and streams the resulting drawing events straight into a browser `<canvas>` in real time.

<div align="center">

```text
> Initializing 0xAirCanvas...
> Camera connected            ✓
> MediaPipe initialized       ✓
> Hand detected               ✓
> Gesture engine online       ✓
> AirCanvas ready. Start drawing ☝️
```

</div>

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/gifs/pixel-line.gif" width="100%">
</div>

## ✨ Features

<table>
<tr>
<td width="33%" align="center">

### 🖐️
**Real-Time Hand Tracking**
21-point landmark detection powered by MediaPipe, live on every frame.

</td>
<td width="33%" align="center">

### ✍️
**Air Writing**
Your fingertip becomes a digital pen — smoothed, low-jitter strokes.

</td>
<td width="33%" align="center">

### 🎨
**Custom Brushes**
Adjustable size, glowing neon-style strokes.

</td>
</tr>
<tr>
<td width="33%" align="center">

### 🌈
**Multiple Colors**
Seven-color palette, switch instantly mid-drawing.

</td>
<td width="33%" align="center">

### 🧹
**Smart Eraser**
Same smoothing pipeline as the brush, adjustable size.

</td>
<td width="33%" align="center">

### ↩️
**Undo / Redo**
Full history stack — step through every stroke.

</td>
</tr>
<tr>
<td width="33%" align="center">

### 💾
**PNG Export**
Save your artwork with one click or a shortcut.

</td>
<td width="33%" align="center">

### 📷
**Camera Selector**
Pick from any connected camera, hot-swap without restarting.

</td>
<td width="33%" align="center">

### 📊
**Live System HUD**
Camera status, hand detection, gesture, FPS — always visible.

</td>
</tr>
</table>

<div align="center">

### 🔒 Local Camera Processing

All video processing happens on your machine. **Nothing is uploaded or stored.**

</div>

## 🕹️ Gesture Guide

<div align="center">

| Gesture | Icon | Action |
|:---:|:---:|:---|
| Index Finger | ☝️ | **Draw** |
| Open Palm | ✋ | **Stop drawing** |
| Fist *(hold)* | ✊ | **Clear canvas** |
| Pinch | 🤏 | **Toggle brush / eraser** |

</div>

> Gestures are debounced — a fist must be held briefly before the canvas clears, so one noisy frame can't wipe your drawing.

## 🧠 How It Works

```mermaid
flowchart TD
    A[📷 Webcam Frame] --> B[🧠 MediaPipe Hand Landmarker]
    B --> C[🖐️ 21 Hand Landmarks<br/>pixel + normalized coords]
    C --> D[☝️ Fingertip Isolation<br/>+ Gesture Classification]
    D --> E[📍 EMA Smoothing<br/>removes jitter]
    E --> F[✍️ Drawing Engine<br/>start / move / end events]
    F --> G[🎨 Browser Canvas<br/>rendered live via SSE]

    style A fill:#0891b2,color:#fff
    style B fill:#00e5ff,color:#04222b
    style C fill:#0891b2,color:#fff
    style D fill:#a855f7,color:#fff
    style E fill:#0891b2,color:#fff
    style F fill:#f472b6,color:#04222b
    style G fill:#34d399,color:#04222b
```

The camera frame streams to the browser as MJPEG (`/video_feed`); stroke and status events push over Server-Sent Events (`/api/events`) — so drawing is rendered entirely by the browser's Canvas API, staying smooth and independent of video frame rate.

## 🧰 Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/-Flask-000000?style=flat-square&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/-OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/-MediaPipe-00E5FF?style=flat-square&logo=google&logoColor=black)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![HTML5](https://img.shields.io/badge/-HTML5%20Canvas-E34F26?style=flat-square&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/-Vanilla%20JS-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![CSS3](https://img.shields.io/badge/-CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)

</div>

## 📦 Installation

<details open>
<summary><b>🖱️ Click to expand setup steps</b></summary>

<br/>

**1. Clone the repo**

```bash
git clone https://github.com/0xAbhi13/0xAirCanvas.git
cd 0xAirCanvas
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

<table>
<tr><th>Windows</th><th>macOS / Linux</th></tr>
<tr>
<td>

```bash
venv\Scripts\activate
```

</td>
<td>

```bash
source venv/bin/activate
```

</td>
</tr>
</table>

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run**

```bash
python app.py
```

Then open the local Flask URL shown in your terminal (typically `http://127.0.0.1:5000`).

> On first run, the hand-tracking model (~8 MB) downloads automatically and is cached locally.

</details>

## ▶️ Usage

```text
1. Launch the app and allow camera access when prompted.
2. ☝️  Raise your index finger to start drawing.
3. ✋  Open your palm to pause without erasing.
4. ✊  Hold a fist briefly to clear the canvas.
5. 🤏  Pinch to toggle between brush and eraser.
6. 🎛️  Use the control panel or shortcuts for color, size, undo/redo, save.
7. 📷  Pick a different camera anytime from the CAMERA panel.
```

## ⌨️ Keyboard Shortcuts

<div align="center">

| Key | Action | Key | Action |
|:---:|:---|:---:|:---|
| <kbd>B</kbd> | Brush | <kbd>Z</kbd> | Undo |
| <kbd>E</kbd> | Eraser | <kbd>Y</kbd> | Redo |
| <kbd>C</kbd> | Clear | <kbd>S</kbd> | Save |
| <kbd>H</kbd> | Help | <kbd>Esc</kbd> | Close modal |

</div>

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
│   ├── hand_tracker.py        # MediaPipe Hands wrapper (legacy + Tasks API)
│   ├── gesture_detector.py    # Gesture classification + debounce
│   └── drawing_engine.py      # Smoothing + stroke event generation
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   └── assets/{logo,favicon}.svg
│
└── assets/
    ├── demo.gif                # add after recording locally
    ├── screenshot.png          # add after recording locally
    └── preview.png             # add after recording locally
```

## 🔒 Privacy

🔒 **Camera processing happens locally.** Your video is not uploaded or stored. 0xAirCanvas makes no network calls with your video data — everything runs inside your own Flask server and browser.

## 🛣️ Future Roadmap

- [ ] Multi-hand drawing
- [ ] Air handwriting recognition
- [ ] Shape recognition
- [ ] AI-assisted drawing
- [ ] Gesture-based shortcuts
- [ ] Drawing replay
- [ ] Advanced brush effects
- [ ] Image import

<div align="center">
<img src="https://raw.githubusercontent.com/Anmol-Baranwal/Cool-GIFs-For-GitHub/main/gifs/pixel-line.gif" width="100%">
</div>

## 👨‍💻 Author

<div align="center">

### Abhishek Jadhav

Creator of 0xAirCanvas — building creative projects with Python, AI, computer vision, and web technologies.

[![GitHub](https://img.shields.io/badge/GitHub-%400xAbhi13-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/0xAbhi13)

</div>

## 📄 License

Released under the [MIT License](LICENSE).

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:A855F7,100:00E5FF&height=120&section=footer" width="100%"/>

**Made with ☝️ and a webcam.**

</div>
