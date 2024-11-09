var senderId = localStorage.getItem("senderId");
var token = localStorage.getItem("token");
var ws = "";

if(token == null || token == undefined){
    window.location.href = "/index/";
}

function getAuthHeaders(){
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    }
}

function showLoader(){
    $(".gif-container").css("display", "block");
}

function hideLoader(){
    $(".gif-container").css("display", "none");
}

function showNoChatMessagesDiv(){
    $(".chat-header").css("display", "none");
}

function hideNoChatMessagesDiv(){
    $(".chat-header").css("display", "block");
}

async function fetchChatMessages(roomId){
    const response = await fetch(
        `/api/chat/${roomId}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
    if (response.ok) {
        const data = await response.json();
        console.log("Chat Messages:", data);
        var ui_elems = $("div.chat-history").find("ul");
        ui_elems.find("li").remove();
        $.each(data, function(idx, value){
            console.log(value);
            var li_elem = "";
            if(value.sender.id == senderId){
                li_elem = `<li class="clearfix">\
                            <div class="message-data text-right">\
                                <span class="message-data-time">${value.sent_at}</span>\
                            </div>\
                            <div class="message other-message float-right">${value.message}</div>\                                    
                        </li>`
            }
            else{
                li_elem = `<li class="clearfix">\
                            <div class="message-data">\
                                <span class="message-data-time">${value.sent_at}</span>\
                            </div>\
                            <div class="message my-message">${value.message}</div>\                                    
                        </li>`
            }
            ui_elems.append(li_elem);
        })
    }

     else {
        console.error('Error fetching data', response.statusText);
    }
}

async function fetchUsers(search_text=""){
    const response = await fetch(`/chat-rooms/?search=${search_text}`, {
        method: "GET",
        headers: getAuthHeaders()
    });
    if(response.ok){
        const data = await response.json();
        console.log(data);
        var ui_elems = $("ul#search-dropdown");
        ui_elems.find("li").remove();
        $.each(data, function(idx, value){
            ui_elems.append(
                `<li id="${value.id}" \
                class="open-chat" data-full-name=${value.full_name} chat-room-id=${value.chat_room_id}>${value.full_name}<li>`
                );
        });
        ui_elems.css("display", "block");
    }
    else{
       console.error('Error fetching users data', response.statusText); 
    }
}

function openChatRoom(chat_room_id){
    if(ws != ""){
        ws.close();
    }
    ws = new WebSocket(`ws://localhost:8000/ws/chat/${chat_room_id}/?token=${token}`);
    bindWebsocketEvents(chat_room_id);
    fetchChatMessages(chat_room_id);
}

async function fetchChats(){
    showLoader();
    const response = await fetch("/api/chat/", {
        method: "GET",
        headers: getAuthHeaders()
    })
    if (response.ok){
        const data = await response.json() // find out why we do this
        if(data.length == 0){
            showNoChatMessagesDiv()
        }
        else{
            hideNoChatMessagesDiv()
            let ui_elems = $("ul.chat-list");
            $.each(data, function(idx, value){
                console.log(value);
                let roomId = value.chat_room_id;
                let receiver_name = "";
                if(value.receiver[0].id == senderId){
                    receiver_name = value.sender.full_name
                }
                else{
                    receiver_name = value.receiver[0].full_name
                }
                var li_elem = `<li class="clearfix single-chat" data-room-id=${roomId} data-full-name=${receiver_name}>\
                    <img src="https://bootdey.com/img/Content/avatar/avatar1.png" alt="avatar">\
                    <div class="about">\
                        <div class="name">${receiver_name} <i class="fa fa-circle online"></i></div>\
                        <div class="status">\
                            <span>${value.message}</span><br>\
                        </div>\                                            
                    </div>\
                    </li>`
                ui_elems.append(li_elem);
                if(ws == ""){
                    $("#user_name").text(receiver_name);

                    // TODO: instead of token in query param, pass it in websocket header
                    // https://ably.com/blog/websocket-authentication#:~:text=While%20the%20WebSocket%20browser%20API,token%20in%20the%20request%20header!
                    openChatRoom(roomId);
                }
            });
        }
    }
    else if(response.status == 401){
       window.location.href = "/index/"; 
    }
    else{
        console.log(response.text)
    }
    hideLoader();
}

async function createNewChat(user_id){
    const response = await fetch("/api/room/", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
            "name": `${user_id}_${senderId}`,
            "room_type": "One To One Chat",
            "members": [
                user_id, senderId
            ]
        })
    })
    if(response.ok){
        let data = await response.json();
        console.log(data);
        roomId = data.id;
        openChatRoom(roomId);
    }
    else{
        console.error("Error when creating new chat", response.statusText); 
    }
}

$(document).on("click", "li.open-chat", function(e){
    let chat_room_id = $(this).attr("chat-room-id");
    $("#user_name").text($(this).data("full-name"));
    if(chat_room_id == "null"){
        createNewChat($(this).attr("id"));
    }
    else{
        openChatRoom(chat_room_id);
    }
});

$(document).on("click", "li.single-chat", function(e){
    let chat_room_id = $(this).data("room-id");
    $("#user_name").text($(this).data("full-name"));
    openChatRoom(chat_room_id);
})

// on click of particular chat, open connection and fetch chat fetchChatMessages
$('#show-register-form').click(function(e) {
    e.preventDefault();
    toggleForms();
});

$("#search-text").on("input", function(e){
    fetchUsers($(this).val());
});

fetchChats();

console.log("Connected")

function bindWebsocketEvents(roomId){
    ws.onmessage = function (event) {
        var ui_elems = $("div.chat-history").find("ul");
        var value = JSON.parse(event.data);
        console.log("message received by client:::" + value);
        if(value.sender_id == senderId){
            li_elem = `<li class="clearfix">\
                        <div class="message-data text-right">\
                            <span class="message-data-time">${value.sent_at}</span>\
                        </div>\
                        <div class="message other-message float-right">${value.message}</div>\                                    
                    </li>`
        }
        else{
            li_elem = `<li class="clearfix">\
                        <div class="message-data">\
                            <span class="message-data-time">${value.sent_at}</span>\
                        </div>\
                        <div class="message my-message">${value.message}</div>\                                    
                    </li>`
        }
        ui_elems.append(li_elem);  
    };

    // TODO: need to handle one thing, on opening of one chat, close the another

    ws.onclose = function (event) {
        console.log("WebSocket connection closed", event.code, event.reason);
        // reconnect 
        ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/?token=${token}`);
        console.log("Server reconnected")
    };
}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    console.log("message sent by client")
    input.value = ''
    event.preventDefault()
}