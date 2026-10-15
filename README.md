# Argon-Jarvis — The Final Form

A voice-first Windows desktop AI team (**JARVIS**, **LYRA**, and **DEX**) that sees, listens, talks, and works 24/7 beside you.

## Download Windows `.exe`
Every push to `main` automatically compiles a standalone `Argon-Jarvis.exe` via **GitHub Actions**:
1. Open the [**Actions** tab](../../actions) or [**Releases** section](../../releases) of this repository.
2. Download **`Argon-Jarvis.exe`** and launch it on Windows 10/11.

## The Six Laws Implemented
- **Voice First**: Speak in English, Tamil, or **Tanglish** (`"Jarvis, naalaikku morning enna schedule?"`). Short and sweet replies by default (`"Yes Master."`), detailed when you ask (`"Explain properly."`). Always 12-hour IST time (`7:40 PM`), with zero brackets or emojis read aloud.
- **Fast (Parallel Action Engine)**: Commands like `"Brave open pannu, YouTube la Parithabangal search pannu"` fire immediately while the sentence goes to the brain.
- **Real & Honest**: Every button works. When screen share is off, Jarvis honestly states `"I cannot see your screen because share is off, Master. Turn it on?"` Risky actions (such as closing heavy background processes) display an **Approval Card** first.
- **Simple**: One Master Switch, clean sidebar, big readable typography, and a floating 24/7 HUD Pill when minimized.
- **Alive (60 FPS UI)**: Hardware-painted pulsing agent orbs with expressive blinking eyes, live 28-bar audio waveform, elapsed-time task loader, and a **Reduced Motion** toggle.
- **Finished**: First-launch onboarding wizard sets your name, preferred title, microphone check, and API keys—nothing is hardcoded.

## The Team
| Agent | Role | Voice & Personality | Default Brain |
| :--- | :--- | :--- | :--- |
| **JARVIS** | Leader & Orchestrator | Calm, coordinates the team, gives final answers (`#00E5FF`) | Groq (`llama-3.3-70b-versatile`) |
| **LYRA** | Companion & Research | Warm, tracks routines, hydration reminders, personal memory (`#FF4D8D`) | Gemini (`gemini-2.5-flash`) |
| **DEX** | Coder & System Engineer | Sharpest mind (`"Give me a task."`), process diagnostics, code (`#10B981`) | NVIDIA NIM (`meta/llama-3.1-70b-instruct`) |

*Includes **Debate Mode** (`"Lyra, Dex - discuss this topic and decide"`), **Shift Sleep/Wake Meters**, and **LM Studio (`qwen3-vl-4b`)** offline local fallback.*

## Local Development
```bash
pip install -r requirements.txt
python main.py
```
