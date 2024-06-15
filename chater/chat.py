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

load_dotenv()

api_key = 'sk-x3nw2tbe5ancuh6q2ocsejp9ts30ggjrqat8ucz1p9gpdh8lj6r7rby8mdbmukvy69'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

translator = Translator()

with open(r'static/intents.json', 'r') as f:
    intents = json.load(f)

FILE = r"static/data.pth"
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

executor = ThreadPoolExecutor(max_workers=5)  # Adjust max_workers as needed


def translate_text(text, dest_language='en'):
    translation = translator.translate(text, dest=dest_language)
    return translation.text


def generate_audio(text, lang='ENG'):
    response = requests.post(
        'https://api.bland.ai/v1/voices/e1289219-0ea2-4f22-a994-c542c2a48a0f/sample',
        headers={
            'Content-Type': 'application/json',
            'authorization': api_key
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


def get_response(sentence):
    bot_name = "Greeta:\n"
    lang = translator.detect(sentence).lang

    translated_sentence = translate_text(sentence)

    sentence = tokenize(translated_sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                responses = random.choice(intent['responses'])
                response_text =  responses
                break

        # Translate response back to the original language
        translated_response = translate_text(response_text, dest_language=lang)

        # Asynchronously generate audio
        audio_future = executor.submit(generate_audio, translated_response)

        # Play audio
        audio_data = audio_future.result(timeout=10)  # Wait for up to 10 seconds
        if audio_data:
            with sf.SoundFile(io.BytesIO(audio_data)) as audio_file:
                audio_array = audio_file.read(dtype='float32')
                sd.play(audio_array, audio_file.samplerate)
                sd.wait()
        else:
            print("Audio generation failed for:", translated_response)

        return  bot_name+translated_response
    else:
        apology = "Sorry, I didn't get it. Can you please rephrase?"
        response_text = apology
        translated_apology = translate_text(response_text, dest_language=lang)

        apology_audio_future = executor.submit(generate_audio, translated_apology)
        audio_data = apology_audio_future.result(timeout=10)
        if audio_data:
            with sf.SoundFile(io.BytesIO(audio_data)) as audio_file:
                audio_array = audio_file.read(dtype='float32')
                sd.play(audio_array, audio_file.samplerate)
                sd.wait()
        else:
            print("Audio generation failed for:", translated_apology)

        return bot_name+translated_apology
