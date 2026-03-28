import json
import os
from datetime import datetime

import cv2

from config import REPORT_DIR


def save_report(frame, analysis, ai_summary=None):
    os.makedirs(REPORT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(REPORT_DIR, f"stance_{timestamp}.png")
    text_path = os.path.join(REPORT_DIR, f"stance_{timestamp}.txt")
    json_path = os.path.join(REPORT_DIR, f"stance_{timestamp}.json")

    cv2.imwrite(image_path, frame)

    report_data = {
        "timestamp": timestamp,
        "score": analysis.get("score"),
        "rating_text": analysis.get("rating_text"),
        "batsman_hand": analysis.get("batsman_hand"),
        "stance_style": analysis.get("stance_style"),
        "corrections": analysis.get("corrections"),
        "metrics": analysis.get("metrics"),
        "ai_summary": ai_summary,
    }

    with open(text_path, "w", encoding="utf-8") as f:
        f.write("CRICKET STANCE REPORT\n")
        f.write("=" * 40 + "\n")
        f.write(f"Timestamp      : {timestamp}\n")
        f.write(f"Score          : {analysis.get('score')}/100\n")
        f.write(f"Rating         : {analysis.get('rating_text')}\n")
        f.write(f"Batting Hand   : {analysis.get('batsman_hand')}\n")
        f.write(f"Stance Style   : {analysis.get('stance_style')}\n\n")

        f.write("Corrections:\n")
        corrections = analysis.get("corrections", [])
        if corrections:
            for i, item in enumerate(corrections, start=1):
                f.write(f"{i}. {item}\n")
        else:
            f.write("None\n")

        f.write("\nMetrics:\n")
        for key, value in analysis.get("metrics", {}).items():
            f.write(f"- {key}: {value}\n")

        if ai_summary:
            f.write("\nAI Coach Summary:\n")
            f.write(ai_summary + "\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return {
        "image": image_path,
        "text": text_path,
        "json": json_path
    }
