const socket = io('https://credit-all-in-one.com/');
const sendButton = document.getElementById('send_button');

const chatContent = document.getElementById("chat-content");
const publisher = document.querySelector(".publisher");
const clientIcons = ['https://storage.googleapis.com/credit-398810-website-image/user_icon/parrot.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/toucan.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/duck.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/cute-hamster.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/dinosaur-egg.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/pegasus.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/jackalope.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/unicorn--v1.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/bumblebee.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/ladybird.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/pony.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/hedgehog.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/sheep.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/calico-cat.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/corgi.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/cat_in_a_box.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/dog.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/aggressive-shark.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/whale.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/crab.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/bear.png',
    'https://storage.googleapis.com/credit-398810-website-image/user_icon/deer.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/elephant.png','https://storage.googleapis.com/credit-398810-website-image/user_icon/giraffe.png'];

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
    
    input.value = '';
    sendButton.disabled = true;
    
    // add client message bubble
    addClientMessage(message, selectedIcon);
    // check the length of client message
    checkInputLen(message)
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
    avatar.src = "https://storage.googleapis.com/credit-398810-website-image/favicon/finn--v1.png";
    avatar.alt = "finn";
    
    let mediaBody = document.createElement("div");
    mediaBody.classList.add("media-body");

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
