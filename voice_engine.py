# ==========================================================
# CAIGS ULTRA AI - VOICE ENGINE (STABLE + CONTROLLED)
# ==========================================================

import pyttsx3
import threading

_engine = None
_engine_lock = threading.Lock()


# ==========================================================
# INITIALIZE ENGINE (SAFE SINGLETON)
# ==========================================================

def _init_engine():

    global _engine

    if _engine is None:
        _engine = pyttsx3.init()

        # Default configuration
        _engine.setProperty("rate", 150)
        _engine.setProperty("volume", 1.0)

        # Try selecting best available voice
        voices = _engine.getProperty("voices")

        if voices:
            # Prefer female voice if available
            for voice in voices:
                if "female" in voice.name.lower():
                    _engine.setProperty("voice", voice.id)
                    break


# ==========================================================
# STOP SPEECH
# ==========================================================

def stop_speaking():
    global _engine
    if _engine:
        try:
            _engine.stop()
        except:
            pass


# ==========================================================
# SPEAK TEXT
# ==========================================================

def speak_text(text, rate=150):

    if not text or len(text.strip()) == 0:
        return False

    try:
        with _engine_lock:

            _init_engine()

            _engine.stop()
            _engine.setProperty("rate", rate)

            _engine.say(text)
            _engine.runAndWait()

        return True

    except Exception:
        return False


# ==========================================================
# SING STYLE SPEECH
# ==========================================================

def sing_text(text):

    if not text:
        return False

    melody_prefix = "La la la... "

    try:
        with _engine_lock:

            _init_engine()

            _engine.stop()
            _engine.setProperty("rate", 120)

            _engine.say(melody_prefix + text)
            _engine.runAndWait()

        return True

    except Exception:
        return False


# ==========================================================
# CHANGE VOICE
# ==========================================================

def set_voice(gender="female"):

    global _engine

    try:
        _init_engine()

        voices = _engine.getProperty("voices")

        for voice in voices:
            if gender.lower() in voice.name.lower():
                _engine.setProperty("voice", voice.id)
                return True

        return False

    except Exception:
        return False


# ==========================================================
# CHANGE SPEED
# ==========================================================

def set_rate(rate):

    global _engine

    try:
        _init_engine()
        _engine.setProperty("rate", rate)
        return True
    except:
        return False