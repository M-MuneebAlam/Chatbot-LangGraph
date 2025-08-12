from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    chat_name: str

def chat_node(state: ChatState):
    messages = state['messages']
    chat_name = state.get('chat_name', 'Untitled Chat')
    response = llm.invoke(messages)
    return {
        "messages": [response],
        "chat_name": chat_name  # This will be persisted in the graph state
    }

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    """
    The correct way to get thread data with chat names from graph state
    """
    all_threads = {}
    
    # Get all unique thread_ids first
    thread_ids = set()
    for checkpoint in checkpointer.list(None):
        cfg = checkpoint.config.get('configurable', {})
        tid = cfg.get('thread_id')
        if tid:
            thread_ids.add(tid)
    
    # Now get the actual state for each thread
    for thread_id in thread_ids:
        try:
            # Get the current state for this thread
            state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
            
            # Extract chat_name from the state values
            chat_name = state.values.get('chat_name', 'Untitled Chat')
            all_threads[thread_id] = chat_name
            
            print(f"Retrieved: thread_id={thread_id}, chat_name={chat_name}")
            
        except Exception as e:
            print(f"Error retrieving state for thread {thread_id}: {e}")
            all_threads[thread_id] = 'Untitled Chat'
    
    return [{"id": tid, "name": all_threads[tid]} for tid in all_threads]

# Alternative approach: Direct database query (if you want to see what's actually stored)
def debug_checkpoint_structure():
    """
    Debug function to see what's actually stored in checkpoints
    """
    print("=== DEBUG: Checkpoint Structure ===")
    for i, checkpoint in enumerate(checkpointer.list(None)):
        if i > 2:  # Only show first 3 for debugging
            break
        print(f"Checkpoint {i}:")
        print(f"  Config: {checkpoint.config}")
        print(f"  Values: {checkpoint.values}")
        print(f"  Has values attr: {hasattr(checkpoint, 'values')}")
        if hasattr(checkpoint, 'values') and checkpoint.values:
            print(f"  Values keys: {checkpoint.values.keys() if checkpoint.values else 'None'}")
        print("---")










# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, Annotated
# from langchain_core.messages import BaseMessage, HumanMessage
# # from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph.message import add_messages
# from dotenv import load_dotenv
# import sqlite3

# load_dotenv()

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
#     chat_name: str

# def chat_node(state: ChatState):
#     messages = state['messages']
#     chat_name = state.get('chat_name', 'Untitled Chat')
#     # Chat_name = state['chat_name']
#     response = llm.invoke(messages)
#     return {
#         "messages": [response],
#         # "chat_name": state[Chat_name]
#         "chat_name": chat_name
#         }

# conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# # Checkpointer
# checkpointer = SqliteSaver(conn=conn)

# graph = StateGraph(ChatState)
# graph.add_node("chat_node", chat_node)
# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# # def retrieve_all_threads():
# #     all_threads = set()
# #     for checkpoint in checkpointer.list(None):
# #         all_threads.add(checkpoint.config['configurable']['thread_id'])

# #     return list(all_threads)

# # def retrieve_all_threads():
# #     all_threads = {}
# #     for checkpoint in checkpointer.list(None):
# #         thread_id = checkpoint.config['configurable']['thread_id']
# #         chat_name = checkpoint.config['configurable'].get('chat_name', 'No name found')
# #         # name = checkpoint.config['configurable'].get('name', '')  # Fallback if no name
# #         all_threads[thread_id] = chat_name  # Using a dict to avoid duplicates by id

#     # return [{"id": tid, "name": all_threads[tid]} for tid in all_threads]

# def retrieve_all_threads():
#     all_threads = {}
#     for checkpoint in checkpointer.list(None):
#         cfg = checkpoint.config.get('configurable', {})
#         tid = cfg.get('thread_id')
#         name = cfg.get('chat_name', 'Untitled Chat')
#         if tid:
#             all_threads[tid] = name
#         print(f"Retrieved: thread_id={tid}, chat_name={name}")
#     return [{"id": tid, "name": all_threads[tid]} for tid in all_threads]



















# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, Annotated
# from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langgraph.graph.message import add_messages
# from dotenv import load_dotenv
# import sqlite3

# load_dotenv()

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
#     chat_name: str

# def chat_node(state: ChatState):
#     messages = state['messages']
#     chat_name = state.get('chat_name', 'Untitled Chat')
#     response = llm.invoke(messages)
#     return {
#         "messages": [response],
#         "chat_name": chat_name
#     }

# # Database setup
# conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# # Create custom table for storing chat metadata
# def init_chat_metadata_table():
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS chat_metadata (
#             thread_id TEXT PRIMARY KEY,
#             chat_name TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
#     conn.commit()

# def save_chat_name(thread_id: str, chat_name: str):
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT OR REPLACE INTO chat_metadata (thread_id, chat_name, updated_at)
#         VALUES (?, ?, CURRENT_TIMESTAMP)
#     ''', (thread_id, chat_name))
#     conn.commit()

# def get_chat_name(thread_id: str) -> str:
#     cursor = conn.cursor()
#     cursor.execute('SELECT chat_name FROM chat_metadata WHERE thread_id = ?', (thread_id,))
#     result = cursor.fetchone()
#     return result[0] if result else 'Untitled Chat'

# # Initialize the table
# init_chat_metadata_table()

# # Checkpointer
# checkpointer = SqliteSaver(conn=conn)

# graph = StateGraph(ChatState)
# graph.add_node("chat_node", chat_node)
# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# def retrieve_all_threads():
#     cursor = conn.cursor()
#     cursor.execute('SELECT thread_id, chat_name FROM chat_metadata ORDER BY updated_at DESC')
#     results = cursor.fetchall()
#     return [{"id": tid, "name": name} for tid, name in results]

# # Custom wrapper for chatbot that saves chat_name
# class ChatbotWrapper:
#     def __init__(self, chatbot, conn):
#         self.chatbot = chatbot
#         self.conn = conn
    
#     def stream(self, input_data, config, **kwargs):
#         # Save chat_name before processing
#         thread_id = config['configurable']['thread_id']
#         chat_name = config['configurable'].get('chat_name', 'Untitled Chat')
#         save_chat_name(thread_id, chat_name)
        
#         # Process with original chatbot
#         return self.chatbot.stream(input_data, config, **kwargs)
    
#     def get_state(self, config):
#         return self.chatbot.get_state(config)

# # Export wrapped chatbot
# chatbot = ChatbotWrapper(chatbot, conn)