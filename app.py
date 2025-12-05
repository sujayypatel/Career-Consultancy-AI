import os
import io
import time
import requests
import json
from flask import Flask, render_template, request, jsonify, send_file, make_response
from dotenv import load_dotenv
from groq import Groq

# 1. Load Environment Variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") 
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

# Initialize Clients
groq_client = Groq(api_key=GROQ_API_KEY)

# OPTIMIZATION: Reuse connections for speed (Keep-Alive)
# This prevents establishing a new SSL handshake for every single request.
session = requests.Session()

# --- STATE MANAGEMENT ---
# Persona: "Life & Career Strategist"
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are 'CareerGenius', an expert Life and Career Strategist. "
            "Your goal is to build a personalized roadmap for the user's dream career. "
            "Follow this conversation flow STRICTLY:\n"
            "1. **Introduction:** Warmly welcome them and ask for their **Name and Age**.\n"
            "2. **Context:** Ask for their **Current Grade/Education Level** (e.g., 10th grade, 2nd year Engineering) and their **Dream Career** (e.g., Astronaut, Founder, AI Engineer).\n"
            "3. **Consultation:** Based on their age and grade, provide a specific, strategic path. Mention:\n"
            "   - Key subjects to master immediately.\n"
            "   - Essential exams (JEE, SAT, GATE, GRE).\n"
            "   - Critical soft skills or projects (e.g., 'Build a dashcam prototype' if they like hardware).\n"
            "4. **Closing:** Ask if they want a detailed timeline for the next 6 months.\n\n"
            "**Constraints:** Keep responses CONCISE (max 2 short sentences). Be encouraging but realistic."
        )
    }
]

# --- HELPER FUNCTIONS ---

def deepgram_stt(audio_buffer):
    """
    Transcribes audio using Deepgram Nova-2 via Raw HTTP.
    OPTIMIZED: Accepts 'audio/webm' for faster uploads.
    """
    url = "https://api.deepgram.com/v1/listen"
    
    # Query Parameters
    params = {
        "model": "nova-2", 
        "smart_format": "true", 
        "language": "en-IN" # Use en-IN for Indian accents
    }
    
    # Headers - Critical for WebM support from Frontend
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/webm" 
    }

    try:
        # Use 'session' to reuse connection
        response = session.post(url, params=params, headers=headers, data=audio_buffer)
        
        if response.status_code == 200:
            return response.json()['results']['channels'][0]['alternatives'][0]['transcript']
        else:
            print(f"Deepgram API Error: {response.text}")
            return ""
            
    except Exception as e:
        print(f"Deepgram Error: {e}")
        return ""

def murf_falcon_tts(text):
    """
    Generates audio using Murf.ai Falcon model via STREAMING endpoint.
    """
    url = "https://global.api.murf.ai/v1/speech/stream"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*", # Accepts raw audio bytes
        "api-key": MURF_API_KEY
    }
    
    payload = {
        "voiceId": "en-US-miles", # Try 'en-US-natalie' for a female voice
        "style": "Conversational",
        "text": text,
        "rate": 0,
        "pitch": 0,
        "sampleRate": 24000,
        "format": "MP3",
        "channelType": "MONO",
        "modelVersion": "FALCON"
    }

    try:
        # Use 'session' to reuse connection
        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.content, None
        return None, f"Murf Error: {response.text}"
            
    except Exception as e:
        return None, f"Request Exception: {str(e)}"

# --- ROUTES ---

@app.route('/')
def index():
    global conversation_history
    # Reset history on refresh so the persona starts fresh
    conversation_history = [conversation_history[0]] 
    return render_template('index.html')

@app.route('/process_voice', methods=['POST'])
def process_voice():
    global conversation_history
    
    # Start Total Timer
    start_total = time.time()
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    buffer = audio_file.read()

    # --- DEBUG: FILE SIZE CHECK ---
    # Look at your terminal! If this is < 100 KB, latency will be instant.
    # If it is > 1000 KB, your frontend is likely still sending WAV.
    print(f"🎤 Received Audio Size: {len(buffer)/1024:.2f} KB")
    # ------------------------------

    # 1. STT (Deepgram)
    t0 = time.time()
    print("--- 1. Transcribing...")
    user_text = deepgram_stt(buffer)
    stt_latency = (time.time() - t0) * 1000
    
    if not user_text:
        return jsonify({"error": "Could not understand audio."}), 400
    
    print(f"User: {user_text} ({stt_latency:.0f}ms)")
    conversation_history.append({"role": "user", "content": user_text})

    # 2. LLM (Groq)
    t1 = time.time()
    print("--- 2. Thinking...")
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation_history,
            temperature=0.7, 
            max_tokens=80    
        )
        ai_response_text = completion.choices[0].message.content
        llm_latency = (time.time() - t1) * 1000
        print(f"AI: {ai_response_text} ({llm_latency:.0f}ms)")
        
        conversation_history.append({"role": "assistant", "content": ai_response_text})
        
    except Exception as e:
        return jsonify({"error": f"Brain Error: {str(e)}"}), 500
    
    t2 = time.time()
    print("--- 3. Speaking...")
    audio_content, error_msg = murf_falcon_tts(ai_response_text)
    tts_latency = (time.time() - t2) * 1000
    
    if audio_content:
        total_latency = (time.time() - start_total) * 1000
        print(f"Total Pipeline: {total_latency:.0f}ms")

        # Create Response with Headers
        response = make_response(send_file(
            io.BytesIO(audio_content),
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="response.mp3"
        ))
        
        # Add Timing Headers for Frontend Stats
        response.headers['X-Latency-STT'] = f"{stt_latency:.0f}"
        response.headers['X-Latency-LLM'] = f"{llm_latency:.0f}"
        response.headers['X-Latency-TTS'] = f"{tts_latency:.0f}"
        response.headers['X-Latency-Total'] = f"{total_latency:.0f}"
        
        return response
    else:
        return jsonify({"error": error_msg or "Voice Generation Failed"}), 500

@app.route('/get_latest_text', methods=['GET'])
def get_latest_text():
    if len(conversation_history) > 1:
        return jsonify({
            "user": conversation_history[-2]['content'],
            "ai": conversation_history[-1]['content']
        })
    return jsonify({"user": "", "ai": ""})

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    print("🚀 CareerGenius (Strategist Mode) Started")
    # Threaded=True prevents the UI status check from blocking the main process
    app.run(debug=True, port=5000, threaded=True)