# anamorphic-chat-app
A real-time end-to-end encrypted chat application using the ElGamal cryptosystem to build Anamorphic Encryption. Every message carries two independent channels — a public message which could be visible if private key is compromised, and a secret message hidden under public message that only the intended recipient can decrypt with double key — all inside a single ciphertext that looks like a normal encryption to any outside observer.

---

## Architecture
 
```
┌─────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                  │
│                                                     │
│  React + Vite                                       │
│  ┌─────────────────┐   ┌─────────────────────────┐  │
│  │   UI Components  │   │    Crypto Layer          │  │
│  │  ChatRoom        │   │  cryptoUtils.js          │  │
│  │  MessageInput    │   │  anamorphicCrypto.js     │  │
│  │  MessageList     │   │                          │  │
│  │  UserList        │   │  - ElGamal PKE           │  │
│  │  AddFriendsModal │   │  - NIZK Mock             │  │
│  │  KeyFileModal    │   │  - Key gen / file I/O    │  │
│  └─────────────────┘   └─────────────────────────┘  │
│                                                     │
│  Keys stored:                                       │
│    aSK     → username_keys.json (downloaded file)   │
│    dkey    → username_keys.json (downloaded file)   │
│    session → in-memory only (_sessionKeys)          │
│    friends → sessionStorage cache                   │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket + REST
┌────────────────────▼────────────────────────────────┐
│                    SERVER (FastAPI)                  │
│                                                     │
│  /auth/signup   /auth/login   /auth/logout          │
│  /friends/list  /friends/add  /friends/available    │
│  /keys/upsert   /keys/get/:username                 │
│  /messages/send /messages/history                   │
│  /ws            (WebSocket)                         │
│                                                     │
│  SQLite DB (chat.db)                                │
│    users       — credentials + active status        │
│    public_keys — dkey (pk0, pk1, sk1, aux)          │
│    messages    — ciphertext only, never plaintext   │
│    friendships — friendship graph                   │
└─────────────────────────────────────────────────────┘
```
 
---


## Tech Stack
 
**Frontend**
- React 18 + Vite
- Tailwind CSS
- Web Crypto API (built-in browser — no external crypto library)
- BigInt for large-number ElGamal arithmetic
- WebSocket for real-time messaging
 
**Backend**
- FastAPI (Python)
- SQLAlchemy (async) + aiosqlite
- SQLite with WAL mode
- JWT authentication (python-jose)
- bcrypt password hashing
- WebSocket for live message delivery
 
---

## Getting Started
 
### Prerequisites
 
- Python 3.11+
- Node.js 18+
 
### Server Setup
 
```bash
cd server
pip install -r requirements.txt
python main.py
```
 
Server runs at `http://localhost:8000`.
 
### Client Setup
 
```bash
cd client
npm install
npm run dev
```
 
App runs at `http://localhost:5173`.
 
---
