import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import mediapipe as mp

from stance_analyzer import analyze_batting_stance
from pose_utils import extract_keypoints, draw_landmarks
from config import *

mp_pose = mp.solutions.pose

st.set_page_config(page_title="Cricket AI Coach", layout="wide")
st.title("🏏 Cricket Stance Detection & Correction")

st.markdown("### 📸 Live Camera Feed")

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=POSE_MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        if results.pose_landmarks:
            draw_landmarks(img, results.pose_landmarks)

            keypoints = extract_keypoints(results.pose_landmarks, img.shape)
            analysis = analyze_batting_stance(keypoints)

            # Display feedback
            cv2.putText(img, f"Score: {analysis['score']}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            y = 70
            for tip in analysis["corrections"]:
                cv2.putText(img, tip, (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                y += 30

        return img

webrtc_streamer(
    key="cricket-ai",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False}
)
