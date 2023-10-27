const socket = io('https://credit-all-in-one.com/');
const sendButton = document.getElementById('send_button');

const chatContent = document.getElementById("chat-content");
const publisher = document.querySelector(".publisher");
const clientIcons = ['https://34.120.182.71/user_icon/parrot.png','https://34.120.182.71/user_icon/toucan.png','https://34.120.182.71/user_icon/duck.png',
    'https://34.120.182.71/user_icon/cute-hamster.png','https://34.120.182.71/user_icon/dinosaur-egg.png','https://34.120.182.71/user_icon/pegasus.png',
    'https://34.120.182.71/user_icon/jackalope.png','https://34.120.182.71/user_icon/unicorn--v1.png','https://34.120.182.71/user_icon/bumblebee.png',
    'https://34.120.182.71/user_icon/ladybird.png','https://34.120.182.71/user_icon/pony.png','https://34.120.182.71/user_icon/hedgehog.png',
    'https://34.120.182.71/user_icon/sheep.png','https://34.120.182.71/user_icon/calico-cat.png','https://34.120.182.71/user_icon/corgi.png',
    'https://34.120.182.71/user_icon/cat_in_a_box.png','https://34.120.182.71/user_icon/dog.png','https://34.120.182.71/user_icon/aggressive-shark.png',
    'https://34.120.182.71/user_icon/whale.png','https://34.120.182.71/user_icon/crab.png','https://34.120.182.71/user_icon/bear.png',
    'https://34.120.182.71/user_icon/deer.png','https://34.120.182.71/user_icon/elephant.png','https://34.120.182.71/user_icon/giraffe.png'];

// random choose a icon for client
let selectedIcon; 
function getRandomIcon() {
    const randomIndex = Math.floor(Math.random() * clientIcons.length); 
    selectedIcon = clientIcons[randomIndex]; 
    // for publisher box
    const iconElement = document.getElementById("selected-icon");
    iconElement.src = selectedIcon;
}
window.addEventListener('load', getRandomIcon); 

// disable the send_button as the input is empty
document.getElementById('message_input').addEventListener('input', function() {
    const input = this;

    if (input.value.trim() === "") {
        sendButton.disabled = true;
    } else {
        sendButton.disabled = false;
    }
});

// send messages to server
function sendMessage() {
    const input = document.getElementById('message_input');
    const sendButton = document.getElementById('send_button');
    const message = [input.value, selectedIcon];
    let suggestedQuestons = document.getElementById('suggested-questions');
    
    input.value = '';
    sendButton.disabled = true;
    
    // add client message bubble
    addClientMessage(message, selectedIcon);
    // check the length of client message
    checkInputLen(message)
    // clean all the suggestedQuestons
    suggestedQuestons.innerHTML = '';
    // make publisher sticked in the bottom
    keepPublisherAtBottom();
    // scroll down
    chatContent.scrollTop = chatContent.scrollHeight;
};


function checkInputLen(message) {
    const input = message[0];
    if (input.length > 150) {
        // prevent the question to server
        addServerMessage('您的訊息內容過長，請調整您的訊息後重新提問。');
    } else {
        // submit to server
        socket.emit('message', message);
    }
}

// waiting and showing marquee
socket.on('calculating', function(calculating) {
    addServerMessage(calculating);
    // make publisher sticked in the bottom
    keepPublisherAtBottom();
    // scroll down
    chatContent.scrollTop = chatContent.scrollHeight;
});

// show results
socket.on('result', function(data) {
    // replace the waiting content into the result
    let lastMediaChat = chatContent.querySelector('.media.media-chat:last-child');
    let lastPTag = lastMediaChat.querySelector('p');
    lastPTag.innerText = data;
});


function keepPublisherAtBottom() {
    publisher.style.position = "relative";
    publisher.style.bottom = "0";
}

function addClientMessage(messageText, icon) {
    let newMessage = document.createElement("div");
    newMessage.classList.add("media", "media-chat", "media-chat-reverse");

    let avatar = document.createElement("img");
    avatar.classList.add("avatar");
    avatar.src = icon;
    avatar.alt = "client";
    
    let mediaBody = document.createElement("div");
    mediaBody.classList.add("media-body", "d-flex", "align-items-center");

    let paragraph = document.createElement("p");
    paragraph.textContent = messageText[0];

    mediaBody.appendChild(paragraph);
    newMessage.appendChild(avatar);
    newMessage.appendChild(mediaBody);

    // add into html element
    chatContent.appendChild(newMessage);
}

function addServerMessage(messageText) {
    let newMessage = document.createElement("div");
    newMessage.classList.add("media", "media-chat");

    let avatar = document.createElement("img");
    avatar.classList.add("avatar");
    avatar.src = "https://34.120.182.71/favicon/finn--v1.png";
    avatar.alt = "finn";
    
    let mediaBody = document.createElement("div");
    mediaBody.classList.add("media-body", "bot-message");

    let paragraph = document.createElement("p");
    paragraph.textContent = messageText;

    mediaBody.appendChild(paragraph);
    newMessage.appendChild(avatar);
    newMessage.appendChild(mediaBody);

    // add into html element
    chatContent.appendChild(newMessage);
}



function addQuestion(button) {
    let suggestedQuestons = document.getElementById('suggested-questions');
    let suggestedQueston = button.innerText;
    let input = document.getElementById('message_input');
    console.log()
    // fill the message input
    input.value = suggestedQueston;
    sendButton.disabled = false;
    // clean all the suggestedQuestons
    suggestedQuestons.innerHTML = '';
}
