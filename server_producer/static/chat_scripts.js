const socket = io();

const chatContent = document.getElementById("chat-content");
const publisher = document.querySelector(".publisher");
const clientIcons = ['https://img.icons8.com/color/48/parrot.png','https://img.icons8.com/color/48/toucan.png','https://img.icons8.com/color/48/duck.png',
    'https://img.icons8.com/color/48/cute-hamster.png','https://img.icons8.com/color/48/dinosaur-egg.png','https://img.icons8.com/color/48/pegasus.png',
    'https://img.icons8.com/color/48/jackalope.png','https://img.icons8.com/color/48/unicorn--v1.png','https://img.icons8.com/color/48/bumblebee.png',
    'https://img.icons8.com/color/48/ladybird.png','https://img.icons8.com/color/48/pony.png','https://img.icons8.com/color/48/hedgehog.png',
    'https://img.icons8.com/color/48/sheep.png','https://img.icons8.com/color/48/calico-cat.png','https://img.icons8.com/color/48/corgi.png',
    'https://img.icons8.com/color/48/cat_in_a_box.png','https://img.icons8.com/color/48/dog.png','https://img.icons8.com/color/48/aggressive-shark.png',
    'https://img.icons8.com/color/48/whale.png','https://img.icons8.com/color/48/crab.png','https://img.icons8.com/color/48/bear.png',
    'https://img.icons8.com/color/48/deer.png','https://img.icons8.com/color/48/elephant.png','https://img.icons8.com/color/48/giraffe.png'];

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


// send messages to server
function sendMessage() {
    const input = document.getElementById('message_input');
    const message = input.value;
    
    if (message.trim() === "") {
        return;
    }

    input.value = '';
    socket.emit('message', message);

    // add client message bubble
    addClientMessage(message, selectedIcon);
    // make publisher sticked in the bottom
    keepPublisherAtBottom();
    // scroll down
    chatContent.scrollTop = chatContent.scrollHeight;
};

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
    var lastMediaChat = chatContent.querySelector('.media.media-chat:last-child');
    var lastPTag = lastMediaChat.querySelector('p');
    lastPTag.innerText = data;
});


function keepPublisherAtBottom() {
    publisher.style.position = "relative";
    publisher.style.bottom = "0";
}

function addClientMessage(messageText, icon) {
    var newMessage = document.createElement("div");
    newMessage.classList.add("media", "media-chat", "media-chat-reverse");

    var avatar = document.createElement("img");
    avatar.classList.add("avatar");
    avatar.src = icon;
    avatar.alt = "client";
    
    var mediaBody = document.createElement("div");
    mediaBody.classList.add("media-body");

    var paragraph = document.createElement("p");
    paragraph.textContent = messageText;

    mediaBody.appendChild(paragraph);
    newMessage.appendChild(avatar);
    newMessage.appendChild(mediaBody);

    // add into html element
    chatContent.appendChild(newMessage);
}

function addServerMessage(messageText) {
    var newMessage = document.createElement("div");
    newMessage.classList.add("media", "media-chat");

    var avatar = document.createElement("img");
    avatar.classList.add("avatar");
    avatar.src = "https://img.icons8.com/color/48/finn--v1.png";
    avatar.alt = "finn";
    
    var mediaBody = document.createElement("div");
    mediaBody.classList.add("media-body");

    var paragraph = document.createElement("p");
    paragraph.textContent = messageText;

    mediaBody.appendChild(paragraph);
    newMessage.appendChild(avatar);
    newMessage.appendChild(mediaBody);

    // add into html element
    chatContent.appendChild(newMessage);
}