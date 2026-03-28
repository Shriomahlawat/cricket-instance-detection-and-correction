import cv2
import mediapipe as mp

from audio_coach import AudioCoach
from config import (
    CAMERA_INDEX,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    INFERENCE_HEIGHT,
    INFERENCE_WIDTH,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    POSE_MODEL_COMPLEXITY,
)
from gpt_coach import GPTCoach
from pose_utils import draw_landmarks, extract_keypoints
from report_utils import save_report
from stance_analyzer import analyze_batting_stance

mp_pose = mp.solutions.pose


def get_score_color(score):
    if score >= 85:
        return (0, 220, 0)
    if score >= 60:
        return (0, 220, 220)
    return (0, 0, 255)


def default_analysis():
    return {
        "score": 0,
        "rating_text": "Stand in front of the camera in batting pose",
        "batsman_hand": "Unknown",
        "stance_style": "Unknown",
        "corrections": ["Keep your full body visible from head to ankles"],
        "metrics": {}
    }


def draw_overlay(frame, analysis, muted, ai_enabled):
    color = get_score_color(analysis["score"])

    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (660, 235), (15, 15, 15), -1)
    cv2.rectangle(overlay, (10, frame.shape[0] - 65), (980, frame.shape[0] - 10), (15, 15, 15), -1)
    frame[:] = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

    y = 40
    cv2.putText(frame, f"Score: {analysis['score']}/100", (25, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.95, color, 2, cv2.LINE_AA)
    y += 35

    cv2.putText(frame, f"Hand: {analysis['batsman_hand']}", (25, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    y += 30

    cv2.putText(frame, f"Style: {analysis['stance_style']}", (25, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    y += 30

    cv2.putText(frame, analysis["rating_text"], (25, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, color, 2, cv2.LINE_AA)
    y += 35

    cv2.putText(frame, "Corrections:", (25, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), 2, cv2.LINE_AA)
    y += 28

    corrections = analysis.get("corrections", [])
    for line in corrections[:3]:
        cv2.putText(frame, f"- {line}", (25, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (230, 230, 230), 2, cv2.LINE_AA)
        y += 28

    audio_status = "Muted" if muted else "On"
    ai_status = "On" if ai_enabled else "Off"
    controls = f"Q Quit | S Save Report | M Mute | Audio: {audio_status} | AI Report: {ai_status}"
    cv2.putText(frame, controls, (25, frame.shape[0] - 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)


def open_camera():
    for idx in [CAMERA_INDEX, 1, 2]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return cap
    return None


def main():
    cap = open_camera()
    if cap is None:
        print("Error: Could not open webcam.")
        return

    audio = AudioCoach()
    ai_coach = GPTCoach()

    last_analysis = default_analysis()

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=POSE_MODEL_COMPLEXITY,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE
    ) as pose:

        print("System started")
        print("Controls: q=quit, s=save report, m=mute/unmute")
        if ai_coach.enabled():
            print(f"AI report enabled with model: {ai_coach.model}")
        else:
            print("AI report disabled (set OPENAI_API_KEY and OPENAI_MODEL if needed)")

        while True:
            ok, frame = cap.read()
            if not ok:
                print("Failed to read frame.")
                break

            frame = cv2.flip(frame, 1)

            infer_frame = cv2.resize(frame, (INFERENCE_WIDTH, INFERENCE_HEIGHT))
            rgb = cv2.cvtColor(infer_frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = pose.process(rgb)
            rgb.flags.writeable = True

            analysis = default_analysis()

            if results.pose_landmarks:
                draw_landmarks(frame, results.pose_landmarks)
                keypoints = extract_keypoints(results.pose_landmarks, frame.shape)
                analysis = analyze_batting_stance(keypoints)
                last_analysis = analysis

                if analysis["score"] >= 90:
                    audio.say_messages([analysis["rating_text"]])
                else:
                    audio.say_messages(analysis["corrections"])

            draw_overlay(frame, analysis, audio.muted, ai_coach.enabled())
            cv2.imshow("Cricket Batting Stance Corrector", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("m"):
                state = audio.toggle_mute()
                print("Audio muted" if state else "Audio unmuted")

            elif key == ord("s"):
                print("Saving report...")
                ai_summary = None

                if ai_coach.enabled():
                    print("Generating AI coaching summary...")
                    ai_summary = ai_coach.generate_report(last_analysis)

                paths = save_report(frame, last_analysis, ai_summary)
                print("Saved:")
                print(" Image:", paths["image"])
                print(" Text :", paths["text"])
                print(" JSON :", paths["json"])

    audio.shutdown()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
