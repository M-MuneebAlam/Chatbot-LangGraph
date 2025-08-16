# LangGraph Chatbot

This project is a conversational chatbot built with **Streamlit** for the frontend and **LangGraph** for the backend.
It integrates **Google's Generative AI (Gemini 2.0 Flash)** through LangChain, with conversation history stored in a **SQLite database** for persistence across sessions.

---

## Features

- Multi-threaded conversations with automatic chat history management.
- Persistent chat history stored in SQLite using LangGraph checkpointing.
- Conversations are named automatically based on the first user message.
- Streamlit frontend with a sidebar for switching between chats.
- Uses Google Generative AI for fast and high quality responses.

---

## Project Structure

```
.
├── frontend.py     # Streamlit frontend
├── backend.py      # LangGraph backend
├── chatbot.db      # SQLite database storing chat history (created at runtime)
├── .env            # Environment variables (API keys, configs)
└── README.md       # Project documentation
```

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/M-MuneebAlam/langgraph-chatbot.git
cd langgraph-chatbot
```

2. **Set up a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Environment Setup

You need a Google Generative AI API key.

1. Create a `.env` file in the project root.
2. Add your key like this:

```
GOOGLE_API_KEY=your_google_api_key_here
```

---

## Running the Project

Start both the backend and frontend.

1. **Backend (LangGraph service)**
   The backend is handled directly within `backend.py`. No separate server is required since Streamlit calls it directly.

2. **Frontend (Streamlit UI)**
   Run:

```bash
streamlit run frontend.py
```

Open the provided URL in your browser to use the chatbot.

---

## Usage

- Click **New Chat** in the sidebar to start a fresh conversation.
- Previous chats are listed under **My Conversations**.
- The name of a chat is updated automatically based on the first user input.
- Chats are stored in SQLite, so you can close and reopen the app without losing history.

---

## How It Works

### Frontend (`frontend.py`)

- Handles chat interactions with the user.
- Manages session state including message history, chat names, and thread IDs.
- Sends user inputs to the backend and streams assistant responses.

### Backend (`backend.py`)

- Defines a `ChatState` that holds messages and chat names.
- Uses LangGraph to manage conversation flow with checkpointing in SQLite.
- Integrates `ChatGoogleGenerativeAI` for generating responses.
- Provides utility functions to retrieve and manage saved chat threads.

---

## Requirements

- Python 3.9+
- Streamlit
- LangChain
- LangGraph
- langchain-google-genai
- sqlite3
- python-dotenv

---

## Example

After launching, you can interact like this:

1. Open the app in your browser.
2. Type a message such as _"Tell me a fun fact about space"_.
3. The assistant responds in real-time.
4. Your chat appears in the sidebar and can be revisited later.

---

## Development Notes

- The chatbot automatically generates unique thread IDs using `uuid4`.
- Chat states are saved with `SqliteSaver` for persistence.
- The backend allows debugging checkpoint structures if needed.
- If a chat has no messages, pressing **New Chat** will not create an empty thread.

---

## Future Improvements

- Add support for user authentication.
- Provide export options for chat histories.
- Allow renaming chats directly from the UI.
- Add multi-LLM support for experimentation.
