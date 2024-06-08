let messageSpoken = false;

document.getElementById("messageButton").addEventListener("click", function() {
    var chatbox = document.querySelector(".chatbox__support");
    chatbox.classList.toggle("chatbox--active");
    if (chatbox.classList.contains("chatbox--active") && !messageSpoken) {
        speakWelcomeMessage();
        messageSpoken = true;
    }
});
function speakWelcomeMessage() {
    var welcomeMessage = "Welcome to Vigilant Site, your guardian in workplace safety! " +
        "I'm here to guide you through our world of safety solutions. " +
        "Whether you're curious about our services, need advice on " +
        "safety practices, or have any other questions, I've got you " +
        "covered. How can I assist you today?";
    
    var speech = new SpeechSynthesisUtterance();
    speech.volume = 1;
    speech.rate = 1.5; 
    speech.pitch = 1;
    speech.text = welcomeMessage;

    var voices = window.speechSynthesis.getVoices();
    var selectedVoice = voices.find(function(voice) {
        return voice.name === 'Microsoft Zira - English (United States)';
    });

    if (selectedVoice) {
        speech.voice = selectedVoice;
    } else {
        console.error('Could not find a suitable female voice.');
    }

    window.speechSynthesis.speak(speech);
}

function playSound() {
    var audio = document.getElementById("clickSound");
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
document.querySelector('.mic-button').addEventListener('click', async function() {
    this.classList.toggle('active');
    playSound();

    try {
        
        const visitorMessage = await convertSpeechToText();

        
        const messagesList = document.querySelector('.chatbox__messages');
        const lastMessage = messagesList.lastElementChild;

        
        const visitorMessageItem = document.createElement('div');
        visitorMessageItem.classList.add('messages__item', 'messages__item--visitor');
        visitorMessageItem.textContent = visitorMessage;

        
        messagesList.insertBefore(visitorMessageItem, lastMessage);
        
        messagesList.scrollTop = 0;

        fetch('', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'message': visitorMessage
            })
        })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.botResponse;  

            // Create a new message item for the bot's response
            const botResponseItem = document.createElement('div');
            botResponseItem.classList.add('messages__item', 'messages__item--operator');
            botResponseItem.textContent = botResponse; 
                    
            // Insert the bot's response after the visitor's message
            messagesList.insertBefore(botResponseItem, visitorMessageItem); // Insert after the visitor's message
                
            messagesList.scrollTop = 0;

            document.querySelector('.message-input').value = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } catch (error) {
        console.error("Error converting speech to text:", error);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.querySelector('.message-form');
    const messageInput = document.querySelector('.message-input');
    const messagesList = document.querySelector('.chatbox__messages');

    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const message = messageInput.value.trim();
        if (message.length === 0) {
            return;
        }

        const messageItem = document.createElement('div');
        messageItem.classList.add('messages__item', 'messages__item--visitor');
        messageItem.textContent = message;

        const lastMessage = messagesList.lastElementChild;
        messagesList.insertBefore(messageItem, lastMessage);

        fetch('', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'message': message
            })
        })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.botResponse;  
                    
            const responseItem = document.createElement('div');
            responseItem.classList.add('messages__item', 'messages__item--operator');
            responseItem.textContent = botResponse; 
                    
            messagesList.insertBefore(responseItem, messageItem); 

            messagesList.scrollTop = 0;
        })
        .catch(error => {
            console.error('Error:', error);
        });

        messageInput.value = '';
    });
});
