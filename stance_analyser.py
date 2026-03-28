from pose_utils import calculate_angle, distance, midpoint, angle_from_vertical


REQUIRED_POINTS = [
    "nose",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
]


def add_feedback(feedback_list, message):
    if message not in feedback_list:
        feedback_list.append(message)


def estimate_batting_hand(kp, shoulder_width):
    margin = max(12, int(shoulder_width * 0.08))

    # In a normal batting grip, the top hand is usually slightly higher
    if kp["left_wrist"]["py"] + margin < kp["right_wrist"]["py"]:
        return "Right-Handed"
    if kp["right_wrist"]["py"] + margin < kp["left_wrist"]["py"]:
        return "Left-Handed"

    # Fallback heuristic
    if kp["left_wrist"]["px"] < kp["right_wrist"]["px"]:
        return "Right-Handed"
    return "Left-Handed"


def classify_stance_style(kp):
    shoulder_turn = abs(kp["left_shoulder"]["z"] - kp["right_shoulder"]["z"])
    hip_turn = abs(kp["left_hip"]["z"] - kp["right_hip"]["z"])
    turn_score = (shoulder_turn + hip_turn) / 2

    if turn_score < 0.08:
        return "Front-On"
    elif turn_score < 0.18:
        return "Open"
    return "Side-On"


def analyze_batting_stance(kp):
    for name in REQUIRED_POINTS:
        if kp[name]["visibility"] < 0.55:
            return {
                "score": 15,
                "rating_text": "Move back so full body is visible",
                "batsman_hand": "Unknown",
                "stance_style": "Unknown",
                "corrections": [
                    "Show head, shoulders, hips, knees, and ankles in frame"
                ],
                "metrics": {}
            }

    left_shoulder = kp["left_shoulder"]
    right_shoulder = kp["right_shoulder"]
    left_elbow = kp["left_elbow"]
    right_elbow = kp["right_elbow"]
    left_wrist = kp["left_wrist"]
    right_wrist = kp["right_wrist"]
    left_hip = kp["left_hip"]
    right_hip = kp["right_hip"]
    left_knee = kp["left_knee"]
    right_knee = kp["right_knee"]
    left_ankle = kp["left_ankle"]
    right_ankle = kp["right_ankle"]
    nose = kp["nose"]

    score = 100
    feedback = []

    shoulder_width = distance(left_shoulder, right_shoulder)
    hip_width = distance(left_hip, right_hip)
    feet_width = distance(left_ankle, right_ankle)
    hand_gap = distance(left_wrist, right_wrist)

    shoulder_mid = midpoint(left_shoulder, right_shoulder)
    hip_mid = midpoint(left_hip, right_hip)
    ankle_mid = midpoint(left_ankle, right_ankle)

    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
    avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

    spine_tilt = angle_from_vertical(shoulder_mid, hip_mid)
    head_offset_ratio = abs(nose["px"] - hip_mid["px"]) / max(shoulder_width, 1)
    base_balance_ratio = abs(hip_mid["px"] - ankle_mid["px"]) / max(shoulder_width, 1)

    batsman_hand = estimate_batting_hand(kp, shoulder_width)
    stance_style = classify_stance_style(kp)

    # Feet width
    if feet_width < shoulder_width * 0.75:
        score -= 12
        add_feedback(feedback, "Spread your feet slightly wider")
    elif feet_width > shoulder_width * 1.75:
        score -= 10
        add_feedback(feedback, "Bring your feet a little closer together")

    # Knee bend
    if avg_knee_angle > 177:
        score -= 18
        add_feedback(feedback, "Bend your knees slightly")
    elif avg_knee_angle < 125:
        score -= 10
        add_feedback(feedback, "Do not crouch too much")

    if abs(left_knee_angle - right_knee_angle) > 20:
        score -= 8
        add_feedback(feedback, "Keep both knees balanced")

    # Arm setup
    if avg_elbow_angle > 170:
        score -= 10
        add_feedback(feedback, "Soften your elbows")
    elif avg_elbow_angle < 60:
        score -= 6
        add_feedback(feedback, "Relax and extend your arms a little")

    if hand_gap > shoulder_width * 0.95:
        score -= 12
        add_feedback(feedback, "Bring your hands closer like holding the bat handle")

    # Head and balance
    if head_offset_ratio > 0.65:
        score -= 12
        add_feedback(feedback, "Keep your head more over your base")

    if spine_tilt > 20:
        score -= 12
        add_feedback(feedback, "Keep your torso more upright")

    if base_balance_ratio > 0.60:
        score -= 10
        add_feedback(feedback, "Center your weight between both feet")

    # Top-hand check
    if batsman_hand == "Right-Handed":
        if left_wrist["py"] > right_wrist["py"] + max(10, int(shoulder_width * 0.06)):
            score -= 8
            add_feedback(feedback, "Keep your left hand slightly above your right hand")
    elif batsman_hand == "Left-Handed":
        if right_wrist["py"] > left_wrist["py"] + max(10, int(shoulder_width * 0.06)):
            score -= 8
            add_feedback(feedback, "Keep your right hand slightly above your left hand")

    score = max(0, min(100, score))

    if score >= 90:
        rating_text = "Excellent batting stance"
        if not feedback:
            feedback.append("Balanced setup, hold this position")
    elif score >= 75:
        rating_text = "Good stance, minor corrections needed"
    elif score >= 55:
        rating_text = "Average stance, improve posture"
    else:
        rating_text = "Poor stance, follow the corrections"

    return {
        "score": score,
        "rating_text": rating_text,
        "batsman_hand": batsman_hand,
        "stance_style": stance_style,
        "corrections": feedback,
        "metrics": {
            "shoulder_width_px": round(shoulder_width, 2),
            "hip_width_px": round(hip_width, 2),
            "feet_width_px": round(feet_width, 2),
            "hand_gap_px": round(hand_gap, 2),
            "left_knee_angle": round(left_knee_angle, 2),
            "right_knee_angle": round(right_knee_angle, 2),
            "left_elbow_angle": round(left_elbow_angle, 2),
            "right_elbow_angle": round(right_elbow_angle, 2),
            "avg_knee_angle": round(avg_knee_angle, 2),
            "avg_elbow_angle": round(avg_elbow_angle, 2),
            "spine_tilt_deg": round(spine_tilt, 2),
            "head_offset_ratio": round(head_offset_ratio, 2),
            "base_balance_ratio": round(base_balance_ratio, 2),
        }
    }
