import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PomodoroAI:
    """
    Klasa do ustalania inteligentnej długości sesji Pomodoro,
    bazując na nastroju, poziomie energii i statystykach.
    """

    def recommend_session_length(self, mood_entry, last_sessions=None):
        """
        Zwraca rekomendowaną długość (w minutach).
        mood_entry: {"energy_level": int, "focus_level": int, "mood": str}
        last_sessions: lista poprzednich sesji, np. [{"actual_duration": 25}, ...]
        """
        base_time = 25  # startowa długość
        energy = mood_entry.get("energy_level", 5)
        focus = mood_entry.get("focus_level", 5)

        # Prosta heurystyka:
        # - Jeśli energy/focus > 7, +5 minut
        # - Jeśli energy/focus < 4, -5 minut
        # - Bierz średnią z ostatnich 3 sesji jako korektę

        if energy > 7 and focus > 7:
            base_time += 5
        elif energy < 4 or focus < 4:
            base_time -= 5

        if base_time < 15:
            base_time = 15  # minimalny czas 15 min

        if last_sessions:
            durations = [s.get("actual_duration", 25) for s in last_sessions if s.get("actual_duration")]
            if durations:
                avg_duration = sum(durations) / len(durations)
                # korekta w oparciu o średnią z poprzednich
                # np. 70% w stronę base_time, 30% w stronę avg_duration
                base_time = int(0.7 * base_time + 0.3 * avg_duration)

        return base_time
