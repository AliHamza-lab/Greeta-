import json
import torch
from .my_nltk_script import bag_of_words, tokenize
from .model import NeuralNet
import random
from googletrans import Translator
import requests
import sounddevice as sd
import soundfile as sf
import io
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import wikipedia 
import re

class ChatBot:
    load_dotenv()
    api_key = os.getenv("API_KEY")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    translator = Translator()

    with open(r'static\intents.json', 'r') as f:
        intents = json.load(f)

    FILE = r"static\data.pth"
    data = torch.load(FILE)
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data["all_words"]
    tags = data["tags"]
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    executor = ThreadPoolExecutor(max_workers=5) 

    translation_cache = {}

    @staticmethod
    def translate_text(text, dest_language='en'):
        if (text, dest_language) in ChatBot.translation_cache:
            return ChatBot.translation_cache[(text, dest_language)]
        
        translation = ChatBot.translator.translate(text, dest=dest_language)
        translated_text = translation.text
        ChatBot.translation_cache[(text, dest_language)] = translated_text
        
        return translated_text

    @staticmethod
    def generate_audio(text, lang='ENG'):
        response = requests.post(
            'https://api.bland.ai/v1/voices/e1289219-0ea2-4f22-a994-c542c2a48a0f/sample',
            headers={
                'Content-Type': 'application/json',
                'authorization': ChatBot.api_key
            },
            json={
                'text': text,
                'voice_settings': {},
                'language': lang
            }
        )
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to generate audio for: {text}. Status code: {response.status_code}")
            return None

    @staticmethod
    def play_audio(audio_data):
        if audio_data:
            with sf.SoundFile(io.BytesIO(audio_data)) as audio_file:
                audio_array = audio_file.read(dtype='float32')
                sd.play(audio_array, audio_file.samplerate)
                sd.wait()
        else:
            print("Audio generation failed")

def get_response(sentence):
    bot_name = "Greeta:\n"
    lang = ChatBot.translator.detect(sentence).lang

    translated_sentence = ChatBot.translate_text(sentence)

    sentence_tokens = tokenize(translated_sentence)
    X = bag_of_words(sentence_tokens, ChatBot.all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(ChatBot.device)

    output = ChatBot.model(X)
    _, predicted = torch.max(output, dim=1)
    tag = ChatBot.tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        response_text = next(intent['responses'][random.choice(range(len(intent['responses'])))]
                             for intent in ChatBot.intents["intents"] if tag == intent["tag"])
    else:
        try:
            response_text = translated_sentence  # Use the translated sentence as the query for Wikipedia
            summary = wikipedia.summary(response_text, sentences=1)
            response_text = re.sub(r',(?![a-zA-Z0-9])', '', summary)
        except wikipedia.exceptions.PageError:
            response_text = "Sorry, the response for the given topic was not found."
        except wikipedia.exceptions.DisambiguationError:
            response_text = "Ambiguous topic! Please provide more specific details."
        except Exception as e:
            response_text = "Sorry, I didn't get it. Can you please rephrase?"
            print("Error:", e)

    translated_response = ChatBot.translate_text(response_text, dest_language=lang)

    audio_future = ChatBot.executor.submit(ChatBot.generate_audio, translated_response)
    try:
        audio_data = audio_future.result(timeout=10)
        ChatBot.play_audio(audio_data)
    except Exception as e:
        print(f"Audio generation error: {e}")

    return bot_name + translated_response
