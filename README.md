<div align="center">

# 🔐 **CipherTalk - Secure Encrypted Chat Application**
![CipherTalk](https://github.com/Anjalimorupoju/ciphertalk/blob/main/banner.png)

</div>

---

## 🚀 **Overview**
CipherTalk is a secure, real-time chat application built with Django and WebSockets, offering end-to-end encryption for all messages.  
It combines military-grade security with instant messaging capabilities to ensure your conversations remain private, fast, and reliable.

---

## 🧭 **How to Clone This Repository**

To get started with CipherTalk locally:

```bash
# Clone the repository from GitHub
git clone https://github.com/Anjalimorupoju/ciphertalk.git

# Move into the project directory
cd ciphertalk
```

---

## ✨ **Features**

### 🔒 **Security Features**
- 🔐 **End-to-End Encryption** – All messages encrypted using **AES-256**  
- 💣 **Self-Destructing Messages** – Optional **auto-expiration** for sensitive messages  
- 🔑 **Secure Key Exchange** – **RSA encryption** ensures safe key distribution  
- 🧩 **Message Integrity** – **Tamper-proof** message verification  

### 💬 **Chat Features**
- ⚡ **Real-time Messaging** – Instant message delivery with **WebSockets**  
- 👥 **Group Chats** – Create and manage **multi-user chat rooms**  
- 🕵️‍♂️ **Private Messaging** – One-on-one **end-to-end encrypted** conversations  
- ✍️ **Typing Indicators** – See when others are typing  
- 🟢 **Online Status** – Track **real-time user presence**  
- ✅ **Message Read Receipts** – Know when your messages are read  
- 💬 **Message Replies** – Reply directly to specific messages  

---

## 🛠️ **Installation**

### ⚙️ **Prerequisites**
- 🐍 Python **3.8+**  
- 🌐 Django **4.0+**  
- 🗄️ PostgreSQL (**recommended**) or SQLite

### 🔹 Step 1: Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 🔹 Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔹 Step 3: Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 🔹 Step 4: Run Development Server
```bash
python manage.py runserver
```

🌍 Visit **http://localhost:8000** to view the app.

---

## 🏗️ **Project Structure**

```bash
ciphertalk/
│
├── manage.py
├── requirements.txt
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .gitignore
│
├── ciphertalk/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/
│   │   ├── admin.py  forms.py  models.py  urls.py  views.py
│   │   ├── templates/users/ (login.html, register.html, profile.html, 2fa.html)
│   │   └── static/users/
│   ├── chat/
│   │   ├── consumers.py  encryption.py  models.py  routing.py  urls.py  views.py
│   │   ├── templates/chat/ (chatroom.html, contacts.html)
│   │   └── static/chat/
│   ├── analytics/
│   │   ├── models.py  urls.py  views.py
│   │   ├── templates/analytics/dashboard.html
│   │   └── static/analytics/
│   └── api/
│       ├── serializers.py  views.py  urls.py  permissions.py
│
├── static/
│   └── css/ js/ img/
└── templates/
    ├── base.html
    └── includes/
```

---

## 💻 **Usage**

### 💬 **Starting a Chat**
1. 🔑 **Register/Login** to your account  
2. 🏠 **Create or Join** a chat room  
3. 👥 **Invite Participants** to join  
4. 💬 **Start Chatting** securely with **end-to-end encryption**

### 🌟 **Quick Highlights**
- ⚡ Real-time Messaging  
- 🔐 AES-256 Encryption  
- 👀 Presence & Typing Indicators  
- 💬 Replies & Read Receipts  

---

## 🔌 **API Endpoints**

### 🔗 **WebSocket**
```
ws://localhost:8000/ws/chat/{room_name}/
```

### 🌐 **REST Endpoints**
- `GET /api/rooms/` – List user chat rooms  
- `GET /api/messages/{room_name}/` – Retrieve chat messages  
- `POST /api/send-message/` – Send a message  
- `GET /api/contacts/` – List all contacts  
- `POST /api/add-contact/` – Add a contact  

---

## 🗄️ **Database Models (Core)**

- 🏠 **ChatRoom** – Chat rooms with participants  
- 💌 **Message** – Encrypted message content and metadata  
- 👤 **Contact** – User contact relationships  
- 🟢 **UserPresence** – Real-time online/offline tracking  

---

## 🔒 **Security Implementation**

### 🔐 **Encryption Flow**
1. **AES-256** encrypts message bodies  
2. **RSA** secures key exchange  
3. **Integrity checks** protect against tampering  
4. **Self-destruct timers** for sensitive messages  

> 💡 **Production Tip:** Set `DEBUG=False`, enable HTTPS, rotate encryption keys regularly, secure cookies, and enforce CSRF protection.

---

## 🚀 **Deployment**

### 📦 **Static Files**
```bash
python manage.py collectstatic
```

### ⚡ **ASGI Server (Daphne Example)**
```bash
daphne ciphertalk.asgi:application --port 8000
```

### 🐳 **Docker (Optional)**
```bash
docker-compose up --build
```

---

## 🧪 **Testing**
```bash
# Run all tests
python manage.py test

# Run tests for chat app only
python manage.py test apps.chat
```

---

## 🆘 **Troubleshooting**

### 🚫 **WebSocket Connection Failed**
- Ensure the **ASGI server** is running  
- Verify **CHANNEL_LAYERS** configuration  
- Check **WebSocket URL patterns**

### 🗄️ **Database Problems**
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

<div align="center">

### 💬 **CipherTalk — Secure Your Conversations** 🔒  
*Built with ❤️ using Django & WebSockets*

</div>
