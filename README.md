<div align="center">



\# 🖐️ 0xAirCanvas



\### ✨ \*\*Write in the Air. Create Without Touch.\*\*



\*\*A futuristic computer-vision canvas that turns your webcam into a digital pen.\*\*



<br>



<img src="https://img.shields.io/badge/Python-3.x-00fff7?style=for-the-badge\&logo=python\&logoColor=white" />

<img src="https://img.shields.io/badge/Flask-Web\_App-00fff7?style=for-the-badge\&logo=flask\&logoColor=white" />

<img src="https://img.shields.io/badge/OpenCV-Computer\_Vision-00fff7?style=for-the-badge\&logo=opencv\&logoColor=white" />

<img src="https://img.shields.io/badge/MediaPipe-Hand\_Tracking-00fff7?style=for-the-badge" />



<br><br>



<img src="https://img.shields.io/github/stars/0xAbhi13/0xAirCanvas?style=for-the-badge\&logo=github\&label=STARS" />

<img src="https://img.shields.io/github/forks/0xAbhi13/0xAirCanvas?style=for-the-badge\&logo=github\&label=FORKS" />

<img src="https://img.shields.io/github/license/0xAbhi13/0xAirCanvas?style=for-the-badge\&label=LICENSE" />



<br><br>



> \*\*Your hand is the controller.

> The air is the canvas.\*\*



<br>



\*\*Created by \[Abhishek Jadhav](https://github.com/0xAbhi13) · \[@0xAbhi13](https://github.com/0xAbhi13)\*\*



</div>



\---



<div align="center">



\## 🖥️ `SYSTEM ONLINE`



```text

╔══════════════════════════════════════════════════════════╗

║                    0xAirCanvas OS                       ║

╠══════════════════════════════════════════════════════════╣

║  > Booting vision engine...                    \[ OK ]   ║

║  > Connecting webcam...                        \[ OK ]   ║

║  > Loading MediaPipe...                        \[ OK ]   ║

║  > Initializing gesture engine...              \[ OK ]   ║

║  > Starting drawing engine...                  \[ OK ]   ║

║  > Canvas interface online...                  \[ OK ]   ║

║                                                          ║

║             🖐️ AIR INTERFACE READY                      ║

╚══════════════════════════════════════════════════════════╝

```



</div>



\---



\# ⚡ What is 0xAirCanvas?



\*\*0xAirCanvas\*\* transforms your webcam into a touch-free digital drawing interface.



Simply raise your \*\*index finger\*\*, move it through the air, and your fingertip becomes a virtual brush.



No mouse.

No stylus.

No touchscreen.



Just your \*\*hand + webcam + imagination\*\*.



The application combines \*\*Flask, OpenCV, MediaPipe and HTML5 Canvas\*\* to detect hand landmarks, understand gestures, smooth fingertip movement and render digital strokes in real time.



\---



\# 🎥 Experience the Interface



<div align="center">



\### 🖐️ `DRAW WITHOUT TOUCHING`



```text

&#x20;            WEBCAM

&#x20;               │

&#x20;               ▼

&#x20;       ┌───────────────┐

&#x20;       │   YOUR HAND   │

&#x20;       └───────┬───────┘

&#x20;               │

&#x20;        ☝️ INDEX FINGER

&#x20;               │

&#x20;               ▼

&#x20;       ┌───────────────┐

&#x20;       │   TRACKING    │

&#x20;       │   + GESTURE   │

&#x20;       └───────┬───────┘

&#x20;               │

&#x20;               ▼

&#x20;       ┌───────────────┐

&#x20;       │  AIR CANVAS   │

&#x20;       │               │

&#x20;       │    ✨ DRAW ✨   │

&#x20;       └───────────────┘

```



> 🎬 \*\*Demo:\*\* Add your recorded `assets/demo.gif` here once available.



</div>



\---



\# ✨ Features



<table>

<tr>

<td width="50%">



\### 🖐️ Real-Time Hand Tracking



Detects \*\*21 hand landmarks\*\* using MediaPipe and tracks your hand continuously through the webcam.



</td>



<td width="50%">



\### ✍️ Air Drawing



Your index fingertip becomes a virtual pen for smooth, touch-free drawing.



</td>

</tr>



<tr>

<td>



\### 🎨 Custom Brushes



Adjust brush size and create glowing digital strokes.



</td>



<td>



\### 🌈 Multiple Colors



Switch between multiple colors instantly while drawing.



</td>

</tr>



<tr>

<td>



\### 🧹 Smart Eraser



Erase parts of your artwork using the same gesture-driven interface.



</td>



<td>



\### ↩️ Undo / Redo



Move backward and forward through your drawing history.



</td>

</tr>



<tr>

<td>



\### 💾 PNG Export



Save your finished artwork directly as a PNG image.



</td>



<td>



\### 📊 Live HUD



Monitor camera status, hand detection, gesture state and FPS.



</td>

</tr>



<tr>

<td>



\### ✨ Futuristic Interface



Glassmorphism, neon effects, animated HUD elements and a cyber-style visual system.



</td>



<td>



\### 🔒 Local Processing



Camera processing happens locally on your machine.



</td>

</tr>

</table>



\---



\# 🕹️ Gesture Control System



<div align="center">



|       Gesture       | Action                   |

| :-----------------: | :----------------------- |

| ☝️ \*\*Index Finger\*\* | ✍️ Draw                  |

|   ✋ \*\*Open Palm\*\*   | 🛑 Stop Drawing          |

|      ✊ \*\*Fist\*\*     | 🧹 Clear Canvas          |

|     🤏 \*\*Pinch\*\*    | 🔄 Toggle Brush / Eraser |



</div>



\### 🧠 Smart Gesture Debouncing



The gesture engine doesn't immediately react to a single noisy frame.



For example, the \*\*fist gesture must be held briefly\*\* before the canvas is cleared.



This helps prevent accidental actions caused by temporary tracking noise.



\---



\# 🧠 How It Works



```text

&#x20;                   📷 WEBCAM

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │     OpenCV      │

&#x20;              │ Frame Capture   │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │    MediaPipe    │

&#x20;              │  Hand Tracking  │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ 21 Hand         │

&#x20;              │ Landmarks       │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ Gesture Detector│

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ Fingertip       │

&#x20;              │ Tracking        │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ Coordinate      │

&#x20;              │ Smoothing       │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ Drawing Engine   │

&#x20;              └────────┬────────┘

&#x20;                       │

&#x20;                       ▼

&#x20;              ┌─────────────────┐

&#x20;              │ HTML5 Canvas    │

&#x20;              │ ✨ DIGITAL ART  │

&#x20;              └─────────────────┘

```



\### 🔥 Under the Hood



1\. \*\*OpenCV\*\* captures frames from the webcam.

2\. \*\*MediaPipe\*\* detects the hand and its 21 landmarks.

3\. The \*\*gesture detector\*\* determines the current hand gesture.

4\. The \*\*index fingertip\*\* is isolated as the drawing cursor.

5\. Coordinate smoothing reduces unwanted jitter.

6\. The \*\*drawing engine\*\* generates stroke events.

7\. The browser renders those strokes on an \*\*HTML5 Canvas\*\*.



\---



\# 🧰 Tech Stack



<div align="center">



|      Technology     | Purpose                  |

| :-----------------: | :----------------------- |

|    🐍 \*\*Python\*\*    | Core application logic   |

|     🌐 \*\*Flask\*\*    | Web application backend  |

|    👁️ \*\*OpenCV\*\*   | Webcam \& computer vision |

|  🖐️ \*\*MediaPipe\*\*  | Hand landmark detection  |

|     🔢 \*\*NumPy\*\*    | Numerical processing     |

| 🎨 \*\*HTML5 Canvas\*\* | Real-time drawing        |

|   ⚡ \*\*JavaScript\*\*  | Frontend interaction     |

|     🎨 \*\*CSS3\*\*     | Futuristic interface     |



</div>



\---



\# 📦 Installation



\## 01 — Clone



```bash

git clone https://github.com/0xAbhi13/0xAirCanvas.git

cd 0xAirCanvas

```



\## 02 — Create Virtual Environment



```bash

python -m venv venv

```



\### Windows



```bash

venv\\Scripts\\activate

```



\## 03 — Install Dependencies



```bash

pip install -r requirements.txt

```



\## 04 — Launch



```bash

python app.py

```



Then open the Flask URL shown in your terminal.



Usually:



```text

http://127.0.0.1:5000

```



\---



\# ▶️ Usage



```text

1\. Launch 0xAirCanvas

&#x20;       ↓

2\. Allow camera access

&#x20;       ↓

3\. Show your hand

&#x20;       ↓

4\. Raise your index finger

&#x20;       ↓

5\. Move your finger through the air

&#x20;       ↓

6\. Watch your artwork appear

&#x20;       ↓

7\. Save your creation as PNG

```



\### 💡 Quick Start



\*\*☝️ Index finger → Draw\*\*



\*\*✋ Open palm → Stop\*\*



\*\*✊ Hold fist → Clear\*\*



\*\*🤏 Pinch → Brush / Eraser\*\*



\---



\# ⌨️ Keyboard Controls



<div align="center">



|  Key  | Command       |

| :---: | :------------ |

|  `B`  | 🖌️ Brush     |

|  `E`  | 🧹 Eraser     |

|  `C`  | 🗑️ Clear     |

|  `Z`  | ↩️ Undo       |

|  `Y`  | ↪️ Redo       |

|  `S`  | 💾 Save       |

|  `H`  | ❓ Help        |

| `ESC` | ❌ Close Modal |



</div>



\---



\# 🗂️ Project Architecture



```text

0xAirCanvas/

│

├── 🐍 app.py

│

├── 📦 requirements.txt

├── 📄 README.md

├── 📜 LICENSE

├── ⚙️ .gitignore

│

├── 🧠 vision/

│   ├── \_\_init\_\_.py

│   ├── hand\_tracker.py

│   ├── gesture\_detector.py

│   └── drawing\_engine.py

│

├── 🌐 templates/

│   └── index.html

│

├── 🎨 static/

│   ├── css/

│   │   └── style.css

│   │

│   ├── js/

│   │   └── app.js

│   │

│   └── assets/

│       ├── logo.svg

│       └── favicon.svg

│

└── 📸 assets/

&#x20;   ├── demo.gif

&#x20;   ├── screenshot.png

&#x20;   └── preview.png

```



\---



\# 🔐 Privacy First



\### Your camera stays yours.



0xAirCanvas processes the camera feed locally through your Flask application.



```text

📷 Camera

&#x20;  │

&#x20;  ▼

💻 Your Computer

&#x20;  │

&#x20;  ├── OpenCV

&#x20;  ├── MediaPipe

&#x20;  └── Flask

&#x20;  │

&#x20;  ▼

🎨 Local Canvas

```



\*\*No camera video is uploaded or stored by 0xAirCanvas.\*\*



\---



\# 🛣️ Roadmap



```text

CURRENT

&#x20; │

&#x20; ├── \[x] Real-time hand tracking

&#x20; ├── \[x] Air drawing

&#x20; ├── \[x] Gesture controls

&#x20; ├── \[x] Custom brushes

&#x20; ├── \[x] Colors

&#x20; ├── \[x] Eraser

&#x20; ├── \[x] Undo / Redo

&#x20; └── \[x] PNG Export

&#x20; │

&#x20; ▼

NEXT

&#x20; │

&#x20; ├── \[ ] Multi-hand drawing

&#x20; ├── \[ ] Shape recognition

&#x20; ├── \[ ] Air handwriting recognition

&#x20; ├── \[ ] Gesture shortcuts

&#x20; ├── \[ ] Drawing replay

&#x20; ├── \[ ] Advanced brush effects

&#x20; ├── \[ ] Image import

&#x20; └── \[ ] AI-assisted drawing

```



\---



\# 🌟 Why 0xAirCanvas?



<div align="center">



\### \*\*Because creativity shouldn't require touching a screen.\*\*



```text

&#x20;     YOUR HAND

&#x20;         ↓

&#x20;     YOUR IDEA

&#x20;         ↓

&#x20;      THE AIR

&#x20;         ↓

&#x20;   ┌─────────────┐

&#x20;   │  0xAirCanvas │

&#x20;   └──────┬──────┘

&#x20;          ↓

&#x20;      ✨ ART ✨

```



</div>



\---



\# 👨‍💻 Created By



<div align="center">



\# Abhishek Jadhav



\### `@0xAbhi13`



\*\*Python · AI · Computer Vision · Web Development\*\*



<br>



\[!\[GitHub](https://img.shields.io/badge/GitHub-0xAbhi13-181717?style=for-the-badge\\\&logo=github)](https://github.com/0xAbhi13)



<br>



> Building creative software projects that turn ideas into experiences.



</div>



\---



\# 📄 License



This project is released under the \*\*MIT License\*\*.



See \[`LICENSE`](LICENSE) for details.



\---



<div align="center">



\### 🖐️ Made with Python, Computer Vision \& Imagination.



\*\*`0xAirCanvas` · `@0xAbhi13`\*\*



<br>



⭐ \*\*Star the repository if you like the project!\*\*



</div>



