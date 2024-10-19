# GREETA

This project features a Guitar Tabs Manager combined with an advanced AI chatbot capable of multilingual conversations. The chatbot uses machine learning to understand user intent, translate queries dynamically, and fetch relevant information from Wikipedia when needed. It also generates and plays audio responses to provide a seamless, hands-free user experience.

## Features

- **Manage Guitar Tabs**: Store, organize, and search for guitar tabs based on song name or artist.
- **Multilingual AI Chatbot**: Communicate with the AI chatbot in multiple languages. It detects the language of your query and responds accordingly.
- **Real-time Translation**: Queries are automatically translated into English for processing, and the response is translated back to the user's language.
- **Audio Response**: The chatbot can generate audio responses using the Bland AI voice API for hands-free interaction.
- **Wikipedia Integration**: If the chatbot cannot answer based on predefined intents, it retrieves relevant information from Wikipedia.
  
## Requirements

- Python 3.8+
- PyTorch
- NLTK
- Google Translate API
- Wikipedia API
- Bland AI API
- Requests
- Dotenv

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AliHamza-lab/Greeta-
   cd GREETA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add API keys**:
   - Create a `.env` file in the root of your project with the following format:
     ```plaintext
     API_KEY=your_bland_ai_api_key
     ```

4. **Download model data**:
   Place your model data (`data.pth`) in the `static/` directory.

5. **Run the chatbot**:
   To start the chatbot, you can call the `get_response` function in your main application:
   ```python
   from chatbot import get_response

   user_input = input("You: ")
   bot_response = get_response(user_input)
   print(bot_response)
   ```

## Usage

1. **Chatting with the AI Bot**:
   - Start typing your questions or requests in any language. The bot will detect the language, translate it for understanding, and provide a response.
   - If the chatbot cannot find a matching intent, it will fetch information from Wikipedia.
   
2. **Audio Response**:
   - The bot can generate audio responses using Bland AI's API. Ensure your API key is properly set in the `.env` file.

## Example

```plaintext
You: How to play Wonderwall?
Greeta: Here's a guide to playing Wonderwall on guitar...
(Audio response is played)
```

## Technologies Used

- **Python**: Core language for the application.
- **PyTorch**: Machine learning framework used for intent classification.
- **Natural Language Toolkit (NLTK)**: Used for tokenizing and processing user input.
- **Google Translate API**: Detects and translates languages dynamically.
- **Wikipedia API**: Fetches summaries for unknown topics.
- **Bland AI**: Generates audio responses for chatbot replies.
- **Requests**: Handles API requests.

