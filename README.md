Cricket Stance Corrector AI
A real-time cricket batting stance correction system built with Python, OpenCV, and MediaPipe.

This project detects body posture from a webcam feed, analyzes batting stance using rule-based heuristics, gives live visual feedback, provides audio coaching, and can save a stance report with an optional OpenAI-generated coaching summary.

Features
Real-time pose detection using MediaPipe
Live batting stance analysis using OpenCV
Audio correction feedback using pyttsx3
Detects likely right-handed or left-handed batting stance
Classifies stance style:
Front-On
Open
Side-On
Color-coded score display
Save screenshot + text report + JSON report
Optional AI-generated saved coaching summary using OpenAI
Anti-spam audio cooldown
Mute/unmute support
Optimized for live webcam performance
Tech Stack
Python 3.10 / 3.11
OpenCV
MediaPipe
NumPy
pyttsx3
OpenAI API (optional)
Project Structure
cricket_stance_corrector_ai/
│
├── main.py
├── config.py
├── pose_utils.py
├── stance_analyzer.py
├── audio_coach.py
├── report_utils.py
├── gpt_coach.py
├── requirements.txt
└── README.md
