import cv2
import numpy as np
import logging
import tensorflow as tf
import librosa
import pyaudio
import os
from huggingface_hub import hf_hub_download
import urllib.request

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    VIDEO_MODEL_REPO = "nateraw/fer"
    VIDEO_MODEL_FILENAME = "emotion_model.h5"
    AUDIO_MODEL_REPO = "nateraw/audio_emotion"
    AUDIO_MODEL_FILENAME = "audio_emotion_model.h5"
    CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"

    def __init__(
        self,
        video_model_path="ai/models/emotion_model.h5",
        audio_model_path="ai/models/audio_emotion_model.h5",
        cascade_path="ai/haarcascade_frontalface_default.xml"
    ):
        os.makedirs(os.path.dirname(video_model_path), exist_ok=True)
        os.makedirs(os.path.dirname(audio_model_path), exist_ok=True)

        if not os.path.exists(cascade_path):
            self._download_file(cascade_path, self.CASCADE_URL)
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        video_model_path = self._ensure_model(video_model_path, self.VIDEO_MODEL_REPO, self.VIDEO_MODEL_FILENAME)
        audio_model_path = self._ensure_model(audio_model_path, self.AUDIO_MODEL_REPO, self.AUDIO_MODEL_FILENAME)

        self.video_emotion_model = self._load_tf_model(video_model_path, "wideo")
        self.audio_emotion_model = self._load_tf_model(audio_model_path, "audio")

        self.emotion_labels = {
            0: 'Angry',
            1: 'Disgust',
            2: 'Fear',
            3: 'Happy',
            4: 'Sad',
            5: 'Surprise',
            6: 'Neutral'
        }

        self.audio_emotion_labels = {
            0: 'Calm',
            1: 'Happy',
            2: 'Sad',
            3: 'Angry'
        }

    def _download_file(self, path, url, retries=3):
        for attempt in range(retries):
            try:
                logger.info(f"Pobieranie pliku: {url}")
                urllib.request.urlretrieve(url, path)
                logger.info("Plik pobrany poprawnie.")
                return
            except Exception as e:
                logger.error(f"Błąd pobierania ({attempt+1}/{retries}): {e}")
        raise RuntimeError(f"Nie udało się pobrać pliku: {url}")

    def _ensure_model(self, local_path, repo_id, filename):
        if not os.path.exists(local_path):
            try:
                logger.info(f"Pobieram model z {repo_id} (plik: {filename})")
                downloaded_path = hf_hub_download(repo_id, filename, local_dir=os.path.dirname(local_path))
                logger.info("Model pobrany poprawnie.")
                return downloaded_path
            except Exception as e:
                logger.error(f"Błąd pobierania modelu: {e}")
                raise RuntimeError(f"Nie udało się pobrać modelu: {repo_id}/{filename}")
        return local_path

    def _load_tf_model(self, path, model_type="modelu"):
        try:
            model = tf.keras.models.load_model(path)
            logger.info(f"Model {model_type} załadowany poprawnie.")
            return model
        except Exception as e:
            logger.error(f"Błąd ładowania {model_type}: {e}")
            return None

    def analyze_video_frame(self, frame):
        if self.video_emotion_model is None:
            logger.warning("Model wideo niedostępny.")
            return "Neutral"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            logger.info("Brak wykrytych twarzy.")
            return "Neutral"

        (x, y, w, h) = faces[0]
        face = cv2.resize(gray[y:y+h, x:x+w], (48, 48)) / 255.0
        face = np.expand_dims(face, axis=(0, -1))

        pred = self.video_emotion_model.predict(face)
        emotion = self.emotion_labels[np.argmax(pred)]
        logger.info(f"Emocja wideo: {emotion}")
        return emotion

    def analyze_audio(self, audio_data, sr=22050):
        if self.audio_emotion_model is None:
            logger.warning("Model audio niedostępny.")
            return "Neutral"

        mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=40)
        mfcc_mean = np.mean(mfcc.T, axis=0)
        input_features = np.expand_dims(mfcc_mean, axis=(0, -1))

        pred = self.audio_emotion_model.predict(input_features)
        emotion = self.audio_emotion_labels[np.argmax(pred)]
        logger.info(f"Emocja audio: {emotion}")
        return emotion

    def capture_audio(self, duration=3, sr=22050):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=sr, input=True, frames_per_buffer=1024)

        frames = []
        logger.info("Nagrywanie audio rozpoczęte.")
        for _ in range(int(sr / 1024 * duration)):
            frames.append(np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16))

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio = np.hstack(frames).astype(np.float32)
        audio /= np.max(np.abs(audio))
        logger.info("Nagrywanie zakończone.")
        return audio
