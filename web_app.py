import eel
import os
import threading
import json
import asyncio
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.Learning import run as LearningRecommender
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Model import FirstLayerDMM
from Backend.ImageGenration import GenerateImage
from Backend.IoT import iot
from Backend.TextToSpeech import TextToSpeech

# Initialize Eel
eel.init('web')

@eel.expose
def process_query(query):
    print(f"User Query: {query}")
    try:
        decisions = FirstLayerDMM(query)
        
        # Learning
        if any(d.startswith("LearningRecommender") for d in decisions):
            text, payload = LearningRecommender(query)
            eel.updateLearningResources(payload.get("recommendations", []))
            return {"text": text, "speech": "Here are some learning resources for you."}

        # Realtime Search
        if any(d.startswith("realtime") for d in decisions):
            ans = RealtimeSearchEngine(query)
            return {"text": ans, "speech": ans}

        # Image Generation
        for d in decisions:
            if d.startswith("generate image"):
                prompt = d.replace("generate image ", "")
                GenerateImage(prompt)
                return {"text": "Image generated!", "speech": "I have generated the image for you."}

        # IoT
        for d in decisions:
            if d.startswith("iot"):
                ans = iot(d.replace("iot ", ""))
                return {"text": ans, "speech": ans}

        # Automation
        if any(d.startswith(x) for x in ["open","close","play","system"] for d in decisions):
            # Automation is async, so we must run it in an event loop
            asyncio.run(Automation(decisions))
            return {"text": "Task executed.", "speech": "Task executed."}

        # General Chatbot
        ans = ChatBot(query)
        return {"text": ans, "speech": ans}

    except Exception as e:
        print(f"Error: {e}")
        return {"text": "An error occurred.", "speech": "I encountered an error."}

@eel.expose
def listen_to_speech():
    text = SpeechRecognition()
    if text:
        return text
    return ""

@eel.expose
def speak_text(text):
    TextToSpeech(text)

def start_app():
    # Start the application
    eel.start('index.html', mode='chrome', size=(1000, 700), cmdline_args=['--disable-web-security'])

if __name__ == "__main__":
    start_app()
