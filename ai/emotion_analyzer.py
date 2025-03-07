import cv2
import numpy as np
import logging
import tensorflow as tf
import librosa
import pyaudio

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """
    Klasa do analizy emocji z dźwięku i wideo.
    Integruje OpenCV, PyAudio, TensorFlow oraz librosa.

    UWAGA:
    - Plik Haar Cascade (haarcascade_frontalface_default.xml) powinien znajdować się w katalogu ai/
      lub wskazany przez parametr cascade_path.
    - Modele (np. emotion_model.h5 oraz audio_emotion_model.h5) powinny być wytrenowane na odpowiednich zbiorach i umieszczone w katalogu ai/models/.
    """

    def __init__(self, video_model_path="ai/models/emotion_model.h5",
                 cascade_path="ai/haarcascade_frontalface_default.xml",
                 audio_model_path="ai/models/audio_emotion_model.h5"):
        # Inicjalizacja wykrywacza twarzy
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Ładowanie modelu emocji wideo
        try:
            self.video_emotion_model = tf.keras.models.load_model(video_model_path)
            logger.info("Wczytano model emocji wideo.")
        except Exception as e:
            logger.error(f"Nie udało się wczytać modelu emocji wideo: {e}")
            self.video_emotion_model = None

        # Ładowanie modelu emocji audio
        try:
            self.audio_emotion_model = tf.keras.models.load_model(audio_model_path)
            logger.info("Wczytano model emocji audio.")
        except Exception as e:
            logger.error(f"Nie udało się wczytać modelu emocji audio: {e}")
            self.audio_emotion_model = None

        # Etykiety emocji dla modelu wideo (np. standard FER-2013)
        self.emotion_labels = {
            0: 'Angry',
            1: 'Disgust',
            2: 'Fear',
            3: 'Happy',
            4: 'Sad',
            5: 'Surprise',
            6: 'Neutral'
        }

        # Przykładowe etykiety emocji dla modelu audio
        self.audio_emotion_labels = {
            0: 'Calm',
            1: 'Happy',
            2: 'Sad',
            3: 'Angry'
        }

    def analyze_video_frame(self, frame):
        """
        Analizuje pojedynczą klatkę wideo i zwraca przewidywaną etykietę emocji.
        Parametry:
          frame - obraz z kamery (format BGR, jak z OpenCV)
        """
        if self.video_emotion_model is None:
            logger.warning("Model wideo nie jest dostępny. Zwracam 'Neutral'.")
            return "Neutral"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            logger.info("Nie wykryto twarzy. Zwracam 'Neutral'.")
            return "Neutral"

        # Przyjmujemy pierwszą wykrytą twarz
        (x, y, w, h) = faces[0]
        face_img = gray[y:y + h, x:x + w]

        # Zmiana rozmiaru do 48x48 pikseli (rozmiar wymagany przez model)
        face_img = cv2.resize(face_img, (48, 48))
        face_img = face_img.astype("float32") / 255.0
        face_img = np.expand_dims(face_img, axis=-1)  # dodaj kanał (1)
        face_img = np.expand_dims(face_img, axis=0)  # dodaj wymiar batch

        # Predykcja emocji
        preds = self.video_emotion_model.predict(face_img)
        emotion_idx = np.argmax(preds)
        emotion = self.emotion_labels.get(emotion_idx, "Neutral")
        logger.info(f"Predykcja emocji: {emotion}")
        return emotion

    def analyze_audio(self, audio_data, sr=22050):
        """
        Analizuje dane audio (waveform) i zwraca przewidywaną etykietę emocji.
        Parametry:
          audio_data - numpy array zawierający surowe dane audio,
          sr - częstotliwość próbkowania (domyślnie 22050 Hz)
        """
        if self.audio_emotion_model is None:
            logger.warning("Model audio nie jest dostępny. Zwracam 'Neutral'.")
            return "Neutral"
        try:
            # Ekstrakcja cech MFCC z audio
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=40)
            mfccs_mean = np.mean(mfccs.T, axis=0)
            # Przygotowanie danych wejściowych dla modelu
            input_features = np.expand_dims(mfccs_mean, axis=0)
            if len(input_features.shape) == 2:
                input_features = np.expand_dims(input_features, axis=-1)
            preds = self.audio_emotion_model.predict(input_features)
            emotion_idx = np.argmax(preds)
            emotion = self.audio_emotion_labels.get(emotion_idx, "Neutral")
            logger.info(f"Predykcja emocji audio: {emotion}")
            return emotion
        except Exception as e:
            logger.error(f"Błąd w analizie audio: {e}")
            return "Neutral"

    def capture_audio(self, duration=3, sr=22050):
        """
        Rejestruje dźwięk z mikrofonu przez określony czas (domyślnie 3 sekundy) i zwraca surowe dane audio jako numpy array.
        Parametry:
          duration - czas nagrywania w sekundach,
          sr - częstotliwość próbkowania
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=sr, input=True, frames_per_buffer=1024)
        frames = []
        num_frames = int(sr / 1024 * duration)
        logger.info("Rozpoczęto nagrywanie audio.")
        for _ in range(num_frames):
            data = stream.read(1024)
            frames.append(np.frombuffer(data, dtype=np.int16))
        stream.stop_stream()
        stream.close()
        p.terminate()
        audio_data = np.hstack(frames).astype(np.float32)
        # Normalizacja sygnału
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        logger.info("Nagrywanie audio zakończone.")
        return audio_data
