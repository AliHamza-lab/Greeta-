document.addEventListener('DOMContentLoaded', (event) => {
    const chatbox = document.querySelector('.chatbox__messages');
    const userInput = document.querySelector('.message-input');
    let messageSpoken = false;

    function prependMessage(type, message) {
        const messagesList = chatbox;

        const messageItem = document.createElement('div');
        messageItem.classList.add('messages__item', `messages__item--${type}`);
        messageItem.textContent = message;

        messagesList.insertBefore(messageItem, messagesList.firstChild);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    function prependThinkingMessage() {
        const messagesList = chatbox;

        const thinkingMessageItem = document.createElement('div');
        thinkingMessageItem.classList.add('messages__item', 'messages__item--operator');
        thinkingMessageItem.textContent = 'Thinking...⏳';
        thinkingMessageItem.id = 'thinkingMessage';

        messagesList.insertBefore(thinkingMessageItem, messagesList.firstChild);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    function updateThinkingMessage(response) {
        const thinkingMessageItem = document.getElementById('thinkingMessage');
        if (thinkingMessageItem) {
            thinkingMessageItem.textContent = response;
            thinkingMessageItem.removeAttribute('id');
        }
    }

    async function fetchBotResponse(message) {
        try {
            const response = await fetch('', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'message': message
                })
            });
            const data = await response.json();
            return data.botResponse;
        } catch (error) {
            console.error('Error:', error);
            return 'Sorry, there was an error processing your message.';
        }
    }

    document.querySelector('.mic-button').addEventListener('click', async function() {
        this.classList.toggle('active');
        playSound();

        try {
            const visitorMessage = await convertSpeechToText();
            prependMessage('visitor', visitorMessage);
            prependThinkingMessage();

            const botResponse = await fetchBotResponse(visitorMessage);
            updateThinkingMessage(botResponse);
        } catch (error) {
            console.error("Error converting speech to text:", error);
            updateThinkingMessage("Sorry, I couldn't understand that. Please try again.");
        }
    });

    document.querySelector('.message-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const message = userInput.value.trim();
        if (message.length === 0) {
            return;
        }

        prependMessage('visitor', message);
        prependThinkingMessage();

        try {
            const botResponse = await fetchBotResponse(message);
            updateThinkingMessage(botResponse);
        } catch (error) {
            console.error('Error fetching bot response:', error);
            updateThinkingMessage("Sorry, there was an error processing your message.");
        }

        userInput.value = '';
    });

    document.getElementById("messageButton").addEventListener("click", function() {
        const chatbox = document.querySelector(".chatbox__support");
        chatbox.classList.toggle("chatbox--active");
        if (chatbox.classList.contains("chatbox--active") && !messageSpoken) {
            speakWelcomeMessage();
            messageSpoken = true;
        }
    });

    function speakWelcomeMessage() {
        const welcomeMessage = "Welcome to Vigilant Site, your guardian in workplace safety! " +
            "I'm here to guide you through our world of safety solutions. " +
            "Whether you're curious about our services, need advice on " +
            "safety practices, or have any other questions, I've got you " +
            "covered. How can I assist you today?";

        const speech = new SpeechSynthesisUtterance();
        speech.volume = 1;
        speech.rate = 1.5;
        speech.pitch = 1;
        speech.text = welcomeMessage;

        const loadVoices = new Promise((resolve) => {
            window.speechSynthesis.onvoiceschanged = resolve;
        });

        loadVoices.then(() => {
            const voices = window.speechSynthesis.getVoices();
            const selectedVoice = voices.find(voice => voice.name === 'Microsoft Zira - English (United States)');

            if (selectedVoice) {
                speech.voice = selectedVoice;
            } else {
                console.error('Could not find a suitable female voice.');
            }

            window.speechSynthesis.speak(speech);
        });
    }

    function playSound() {
        const audio = document.getElementById("clickSound");
        audio.play();
    }

    async function convertSpeechToText() {
        return new Promise((resolve, reject) => {
            const recognition = new window.webkitSpeechRecognition();
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                resolve(transcript);
            };

            recognition.onerror = function(event) {
                reject(event.error);
            };

            recognition.start();
        });
    }
});
