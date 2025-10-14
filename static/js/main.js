// =============================
// CipherTalk WebSocket Chat JS
// =============================

class CipherTalkChat {
    constructor() {
        // Variables passed from Django template
        this.roomName = window.roomName;
        this.userId = window.userId;
        this.username = window.username;
        this.roomType = window.roomType;
        this.participants = window.participants || [];

        this.socket = null;
        this.typingTimer = null;
        this.typing = false;
        this.onlineUsers = new Set();

        // Initialize features
        this.initializeSocket();
        this.initializeEventListeners();
        this.scrollToBottom();
        this.initializePresence();
    }

    // -----------------------------
    // 1. WebSocket Connection Setup - FIXED URL
    // -----------------------------
    initializeSocket() {
        // ✅ FIXED: Use encoded room name in URL
        const encodedRoomName = encodeURIComponent(this.roomName);
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${encodedRoomName}/`;

        console.log("🔗 Connecting to WebSocket:", wsUrl);
    
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log("✅ Connected to chat WebSocket");
            this.showSystemMessage("Connected to chat");
            this.updateOnlineStatus(this.userId, true);
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleSocketMessage(data);
            } catch (error) {
                console.error("❌ Error parsing WebSocket message:", error);
            }
        };

        this.socket.onclose = (event) => {
            console.warn("⚠️ WebSocket connection closed:", event.code, event.reason);
            this.showSystemMessage("Connection lost. Reconnecting...");
            this.updateOnlineStatus(this.userId, false);
            setTimeout(() => this.initializeSocket(), 3000);
        };

        this.socket.onerror = (error) => {
            console.error("❌ WebSocket error:", error);
        };
    }

    // -----------------------------
    // 2. Input & Send Event Handlers
    // -----------------------------
    initializeEventListeners() {
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");

        // Add null checks
        if (!messageInput || !sendButton) {
            console.error("❌ Required DOM elements not found");
            return;
        }

        // Resize textarea dynamically
        messageInput.addEventListener("input", () => {
            messageInput.style.height = "auto";
            messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
            this.updateSendButton();
            this.startTyping();
        });

        // Send message with Enter
        messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Start/stop typing indicator
        messageInput.addEventListener("focus", () => this.startTyping());
        messageInput.addEventListener("blur", () => this.stopTyping());

        // Send button click
        sendButton.addEventListener("click", () => this.sendMessage());
    }

    updateSendButton() {
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");
        
        // Add null checks
        if (!messageInput || !sendButton) return;
        
        sendButton.disabled = messageInput.value.trim() === "";
    }

    // -----------------------------
    // 3. Typing Indicator
    // -----------------------------
    startTyping() {
        if (!this.typing && this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.typing = true;
            this.socket.send(JSON.stringify({ 
                type: "typing_start",
                room_name: this.roomName
            }));
        }
        clearTimeout(this.typingTimer);
        this.typingTimer = setTimeout(() => this.stopTyping(), 3000);
    }

    stopTyping() {
        if (this.typing && this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.typing = false;
            this.socket.send(JSON.stringify({ 
                type: "typing_stop",
                room_name: this.roomName
            }));
        }
        clearTimeout(this.typingTimer);
    }

    // -----------------------------
    // 4. Sending Messages
    // -----------------------------
    sendMessage() {
        const messageInput = document.getElementById("messageInput");
        const sendButton = document.getElementById("sendButton");
        
        // Add null checks
        if (!messageInput || !sendButton) return;
        
        const content = messageInput.value.trim();
        if (!content || !this.socket || this.socket.readyState !== WebSocket.OPEN) return;

        const messageData = {
            type: "chat_message",
            message: content,
            room_name: this.roomName,
            sender_id: this.userId,
            username: this.username
        };

        this.socket.send(JSON.stringify(messageData));

        // Reset input
        messageInput.value = "";
        messageInput.style.height = "auto";
        this.updateSendButton();
        this.stopTyping();
    }

    // -----------------------------
    // 5. Handling Incoming Events
    // -----------------------------
    handleSocketMessage(data) {
        switch (data.type) {
            case "chat_message":
                this.displayMessage(data);
                break;
            case "user_joined":
                this.handleUserJoined(data);
                break;
            case "user_left":
                this.handleUserLeft(data);
                break;
            case "user_presence":
                this.handleUserPresence(data);
                break;
            case "typing_indicator":
                this.handleTypingIndicator(data);
                break;
            case "message_read":
                this.handleMessageRead(data);
                break;
            case "online_users":
                this.handleOnlineUsers(data);
                break;
            case "error":
                this.showSystemMessage(`Error: ${data.error}`, true);
                break;
        }
    }

    // -----------------------------
    // 6. Displaying Messages
    // -----------------------------
    displayMessage(data) {
        const messagesContainer = document.getElementById("messagesContainer");
        if (!messagesContainer) return;
        
        const isSent = data.sender_id === this.userId;

        const messageElement = document.createElement("div");
        messageElement.className = `message ${isSent ? "sent" : "received"}`;
        if (data.message_id) {
            messageElement.dataset.messageId = data.message_id;
        }

        const messageBubble = document.createElement("div");
        messageBubble.className = "message-bubble";

        // Add sender name for received messages in group chats
        if (!isSent && this.roomType !== 'private') {
            const senderDiv = document.createElement("div");
            senderDiv.className = "message-sender";
            senderDiv.textContent = data.username || 'Unknown User';
            messageBubble.appendChild(senderDiv);
        }

        // Message content
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        
        // Display the actual message content, not encrypted data
        if (data.message) {
            contentDiv.textContent = data.message;
        } else if (data.encrypted_content) {
            // If only encrypted content is available, show a placeholder
            contentDiv.textContent = "🔒 Encrypted message";
            contentDiv.style.fontStyle = 'italic';
            contentDiv.style.opacity = '0.8';
        } else {
            contentDiv.textContent = "Empty message";
        }

        // Message metadata (time + status)
        const metaDiv = document.createElement("div");
        metaDiv.className = "message-meta";

        const timeSpan = document.createElement("span");
        timeSpan.className = "message-time";
        timeSpan.textContent = this.formatTime(data.timestamp);

        metaDiv.appendChild(timeSpan);

        // Add status indicator for sent messages
        if (isSent) {
            const statusSpan = document.createElement("span");
            statusSpan.className = "message-status";
            statusSpan.innerHTML = data.is_read ? 
                '<i class="fas fa-check-double"></i>' : 
                '<i class="fas fa-check"></i>';
            metaDiv.appendChild(statusSpan);
        }

        messageBubble.appendChild(contentDiv);
        messageBubble.appendChild(metaDiv);
        messageElement.appendChild(messageBubble);
        messagesContainer.appendChild(messageElement);

        this.scrollToBottom();

        // Mark received messages as read
        if (!isSent && data.message_id && this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: "message_read",
                message_id: data.message_id,
                room_name: this.roomName
            }));
        }
    }

    // -----------------------------
    // 7. System Messages
    // -----------------------------
    showSystemMessage(content, isError = false) {
        const messagesContainer = document.getElementById("messagesContainer");
        if (!messagesContainer) return;
        
        const messageElement = document.createElement("div");
        messageElement.className = "message system";

        const messageBubble = document.createElement("div");
        messageBubble.className = "message-bubble";
        messageBubble.textContent = content;

        if (isError) {
            messageBubble.style.background = "#fed7d7";
            messageBubble.style.color = "#c53030";
        }

        messageElement.appendChild(messageBubble);
        messagesContainer.appendChild(messageElement);

        this.scrollToBottom();
    }

    // -----------------------------
    // 8. Typing Indicator Display
    // -----------------------------
    handleTypingIndicator(data) {
        const typingIndicator = document.getElementById("typingIndicator");
        const typingUsers = document.getElementById("typingUsers");

        if (!typingIndicator || !typingUsers) return;

        if (data.typing && data.user_id !== this.userId) {
            typingUsers.textContent = `${data.username} is typing...`;
            typingIndicator.style.display = "flex";
        } else {
            typingIndicator.style.display = "none";
        }
    }

    // -----------------------------
    // 9. Mark Message as Read
    // -----------------------------
    handleMessageRead(data) {
        if (!data.message_id) return;
        
        const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
        if (messageElement) {
            const statusIcon = messageElement.querySelector(".message-status i");
            if (statusIcon) {
                statusIcon.className = "fas fa-check-double";
                statusIcon.style.color = "#48bb78";
            }
        }
    }

    // -----------------------------
    // 10. Presence & Online Status
    // -----------------------------
    initializePresence() {
        // Set initial online status for current user
        this.updateOnlineStatus(this.userId, true);
    }

    handleUserJoined(data) {
        this.showSystemMessage(`${data.username} joined the chat`);
        this.updateOnlineStatus(data.user_id, true);
    }

    handleUserLeft(data) {
        this.showSystemMessage(`${data.username} left the chat`);
        this.updateOnlineStatus(data.user_id, false);
    }

    handleUserPresence(data) {
        this.updateOnlineStatus(data.user_id, data.online);
    }

    handleOnlineUsers(data) {
        this.onlineUsers = new Set(data.users || []);
        this.updateOnlineDisplay();
    }

    updateOnlineStatus(userId, isOnline) {
        const statusElement = document.getElementById(`status-${userId}`);
        const statusTextElement = document.getElementById(`status-text-${userId}`);
        
        if (statusElement) {
            statusElement.style.background = isOnline ? "#48bb78" : "#a0aec0";
        }
        
        if (statusTextElement) {
            statusTextElement.textContent = isOnline ? "Online" : "Offline";
            statusTextElement.style.color = isOnline ? "#48bb78" : "#a0aec0";
        }

        if (isOnline) {
            this.onlineUsers.add(userId);
        } else {
            this.onlineUsers.delete(userId);
        }
        
        this.updateOnlineDisplay();
    }

    updateOnlineDisplay() {
        const onlineCount = this.onlineUsers.size;
        const onlineUsersElement = document.getElementById("onlineUsers");
        const partnerStatusElement = document.getElementById("partnerStatus");
        
        if (onlineUsersElement) {
            onlineUsersElement.textContent = `${onlineCount} online`;
        }
        
        if (partnerStatusElement && this.roomType === 'private') {
            // For private chats, show if the other person is online
            const otherUsers = this.participants.filter(p => p.id !== this.userId);
            const isPartnerOnline = otherUsers.some(user => this.onlineUsers.has(user.id));
            partnerStatusElement.textContent = isPartnerOnline ? "Online" : "Offline";
            partnerStatusElement.style.color = isPartnerOnline ? "#48bb78" : "#a0aec0";
        }
    }

    // -----------------------------
    // 11. Utility Functions
    // -----------------------------
    formatTime(timestamp) {
        if (!timestamp) {
            return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        }
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        } catch (e) {
            return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById("messagesContainer");
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
}

// Initialize chat after DOM loads
document.addEventListener("DOMContentLoaded", () => {
    try {
        // Check if required variables are available
        if (!window.roomName || !window.userId || !window.username) {
            console.error("❌ Missing required chat configuration variables");
            return;
        }
        
        window.chatApp = new CipherTalkChat();
        console.log("✅ CipherTalk chat initialized successfully");
    } catch (error) {
        console.error("❌ Failed to initialize CipherTalk chat:", error);
    }
});

// Scroll to bottom again if user switches back to tab
document.addEventListener("visibilitychange", () => {
    if (!document.hidden && window.chatApp) {
        window.chatApp.scrollToBottom();
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.chatApp && window.chatApp.socket) {
        // Send leave message if possible
        if (window.chatApp.socket.readyState === WebSocket.OPEN) {
            try {
                window.chatApp.socket.send(JSON.stringify({
                    type: "user_left",
                    room_name: window.chatApp.roomName,
                    user_id: window.chatApp.userId,
                    username: window.chatApp.username
                }));
            } catch (error) {
                console.log("Could not send leave message:", error);
            }
        }
    }
});