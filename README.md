# ADHD Support App (Advanced)

Ta wersja zawiera:
- **Inteligentny Pomodoro** z rekomendacją długości sesji (klasa `PomodoroAI`),
- **Rozszerzony Mood Tracker** z poziomem energii, skupienia i placeholderem do analizy emocji (audio/wideo),
- **Baza danych** poszerzona o tabelę `pomodoro_sessions`, pola `focus_score` w `tasks` i `energy_level/focus_level` w `moods`,
- **Dock** w interfejsie do Pomodoro.

## Instalacja
1. Sklonuj repozytorium
2. `pip install -r requirements.txt`
3. `python main.py`

## Użycie
1. Zakładka *Zadania* – standardowe zarządzanie. 
2. Zakładka *Nastrój* – rejestrowanie stanu emocjonalnego + energii/fokusu.
3. *Kalendarz* – przegląd zadań i nastrojów na wybrany dzień.
4. *Pomodoro (Dock)* – w dolnej części okna (można włączyć/wyłączyć). Dla wybranego zadania tworzy się sesja pomodoro.  
   - **Inteligentna rekomendacja** – na podstawie heurystyki (`ai/pomodoro_ai.py`).

## Rozwijanie
- Aby faktycznie analizować emocje z mikrofonu/kamery, rozwiń `EmotionAnalyzer`.
- Dodaj integrację z GPT (np. generowanie raportów głosem).
- Rozbuduj algorytmy w `PomodoroAI` (uczenie maszynowe z danymi nastroju).

Miłej zabawy i pamiętaj – w razie czego minimalizm zawsze wygrywa z przesadną liczbą feature’ów! 
