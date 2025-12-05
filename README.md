CareerGenius AI - Real-time Voice Career Strategist 🚀

CareerGenius AI is an intelligent, real-time voice consultant designed to democratize career counseling in India. It acts as a personal "Life & Career Strategist," helping students identify their dream careers and building personalized roadmaps—all through a natural voice conversation.

Built for the Techfest, IIT Bombay x Murf.ai Voice Agent Hackathon 2025-26.

🛑 The Problem: Biased & Expensive Consulting

In India, the career counseling industry is often plagued by bias. "Free" consultants often push students into specific private colleges purely to earn commissions, ignoring the student's actual potential or interests. Genuine, unbiased mentorship is either inaccessible or prohibitively expensive.

💡 The Solution: CareerGenius AI

CareerGenius provides unbiased, data-driven, and free career strategy to anyone with a smartphone.

It Listens: Understands your age, grade, and deep ambitions (e.g., "I want to be an Astronaut").

It Thinks: Generates a strategic roadmap (exams to take, subjects to master, skills to build).

It Speaks: Responds in real-time with a human-like voice, making advice feel personal and empathetic.

⚡ Tech Stack (The "Speed" Architecture)

To achieve a <500ms response time, we optimized every layer of the stack:

Component

Technology

Why?

Ears (ASR)

Deepgram Nova-2

Fastest transcription API available. Tuned for Indian English.

Brain (LLM)

Llama 3 (via Groq)

Runs on LPUs (Language Processing Units) for sub-second reasoning.

Mouth (TTS)

Murf.ai Falcon

Ultra-low latency streaming TTS. Delivers audio chunks instantly.

Transport

WebM (Opus)

Compresses audio by 20x to minimize upload latency.

🚀 Features

Real-time Conversation: Talk naturally without hitting buttons. The AI detects silence and responds instantly.

Visual Feedback: Live audio visualizer and "Thinking" states for a polished UX.

Latency Metrics: Live display of Ear, Brain, and Mouth latency on the dashboard.

Strategist Persona: Goes beyond generic advice to suggest specific exams (JEE, GATE, SAT) and soft skills.

🛠️ Setup Instructions

1. Clone the Repository
   
git clone https://github.com/sujayypatel/Career-Consultancy-AI.git
cd Career-Consultancy-AI.git


3. Install Dependencies

pip install -r requirements.txt


3. Configure API Keys

Create a .env file in the root directory and add your keys:

GROQ_API_KEY=gsk_...
DEEPGRAM_API_KEY=...
MURF_API_KEY=...


4. Run the Application

python app.py


Open your browser and navigate to http://127.0.0.1:5000.

🧩 API Integration Details

Murf Falcon Integration

We utilize the Murf Falcon model via the Streaming Endpoint to ensure minimum latency.

Endpoint: https://api.murf.ai/v1/speech/stream

Model: FALCON

Voice: en-US-miles (Conversational Style)

Format: MP3 (Streamed directly to frontend)

Latency Optimization Strategy

Network Reuse: Using requests.Session() to keep TCP connections alive.

Audio Compression: Frontend forces audio/webm recording (50KB) instead of WAV (5MB).

VAD Tuning: Silence threshold reduced to 800ms for snappier turn-taking.

👨‍💻 About the Creator

Built by Sujay Patel, a 2nd-year Mechanical Engineering student at DDU and founder of Avantus. Passionate about using AI to solve real-world problems in education and accessibility.

Tags: #murf-ai #voiceagent #hackathon #python #deepgram #groq
