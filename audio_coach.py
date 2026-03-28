import queue
import re
import threading
import time

import pyttsx3

from config import AUDIO_COOLDOWN_SECONDS


class AudioCoach:
    def __init__(self):
        self.muted = False
        self.cooldowns = {}
        self.speech_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.available = True

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 175)
        except Exception:
            self.available = False
            self.engine = None

        if self.available:
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()

    def _clean_text(self, text):
        text = re.sub(r"[^\x00-\x7F]+", "", text)
        text = text.replace("-", " ")
        return text.strip()

    def _run(self):
        while not self.stop_event.is_set():
            try:
                text = self.speech_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if text is None:
                break

            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

            self.speech_queue.task_done()

    def say_messages(self, messages):
        if not self.available or self.muted or not messages:
            return

        now = time.time()

        for msg in messages:
            clean_msg = self._clean_text(msg)
            if not clean_msg:
                continue

            last_time = self.cooldowns.get(clean_msg, 0)
            if now - last_time >= AUDIO_COOLDOWN_SECONDS:
                self.cooldowns[clean_msg] = now

                # keep queue short so audio never lags badly
                if self.speech_queue.qsize() < 2:
                    self.speech_queue.put(clean_msg)
                break

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def shutdown(self):
        self.stop_event.set()
        if self.available:
            self.speech_queue.put(None)
            try:
                self.engine.stop()
            except Exception:
                pass
