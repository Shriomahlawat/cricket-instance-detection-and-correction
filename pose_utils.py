import math
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

LANDMARK_MAP = {
    "nose": mp_pose.PoseLandmark.NOSE.value,
    "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER.value,
    "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
    "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW.value,
    "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW.value,
    "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST.value,
    "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST.value,
    "left_hip": mp_pose.PoseLandmark.LEFT_HIP.value,
    "right_hip": mp_pose.PoseLandmark.RIGHT_HIP.value,
    "left_knee": mp_pose.PoseLandmark.LEFT_KNEE.value,
    "right_knee": mp_pose.PoseLandmark.RIGHT_KNEE.value,
    "left_ankle": mp_pose.PoseLandmark.LEFT_ANKLE.value,
    "right_ankle": mp_pose.PoseLandmark.RIGHT_ANKLE.value,
}


def draw_landmarks(frame, pose_landmarks):
    mp_drawing.draw_landmarks(
        frame,
        pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(0, 140, 255), thickness=2, circle_radius=2),
    )


def extract_keypoints(pose_landmarks, frame_shape):
    h, w = frame_shape[:2]
    landmarks = pose_landmarks.landmark
    points = {}

    for name, idx in LANDMARK_MAP.items():
        lm = landmarks[idx]
        points[name] = {
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "px": int(lm.x * w),
            "py": int(lm.y * h),
            "visibility": lm.visibility,
        }

    return points


def _coords(p):
    if "px" in p and "py" in p:
        return p["px"], p["py"]
    return p["x"], p["y"]


def calculate_angle(a, b, c):
    ax, ay = _coords(a)
    bx, by = _coords(b)
    cx, cy = _coords(c)

    angle = math.degrees(
        math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx)
    )
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
    return angle


def distance(a, b):
    ax, ay = _coords(a)
    bx, by = _coords(b)
    return math.hypot(bx - ax, by - ay)


def midpoint(a, b):
    ax, ay = _coords(a)
    bx, by = _coords(b)

    x = (a["x"] + b["x"]) / 2
    y = (a["y"] + b["y"]) / 2
    z = (a["z"] + b["z"]) / 2

    return {
        "x": x,
        "y": y,
        "z": z,
        "px": int((ax + bx) / 2),
        "py": int((ay + by) / 2),
        "visibility": min(a["visibility"], b["visibility"]),
    }


def angle_from_vertical(top_point, bottom_point):
    tx, ty = _coords(top_point)
    bx, by = _coords(bottom_point)

    dx = tx - bx
    dy = by - ty

    return abs(math.degrees(math.atan2(dx, dy)))
