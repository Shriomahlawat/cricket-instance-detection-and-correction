import os

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Smaller inference size for better performance
INFERENCE_WIDTH = 960
INFERENCE_HEIGHT = 540

POSE_MODEL_COMPLEXITY = 1
MIN_DETECTION_CONFIDENCE = 0.55
MIN_TRACKING_CONFIDENCE = 0.55

VISIBILITY_THRESHOLD = 0.55
AUDIO_COOLDOWN_SECONDS = 7

REPORT_DIR = "reports"
#please create an .env and put your openai api keys there

# OPENAI_MODEL = gpt-5.4
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
