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

def generate_chat_name(first_message: str) -> str:
    """Generate a meaningful chat name based on the first user message"""
    try:
        # Use the LLM to generate a concise chat title
        prompt = f"""Based on this user message, create a short, descriptive title (max 4-5 words) for this chat conversation:

User message: "{first_message}"

Requirements:
- Keep it under 30 characters
- Make it descriptive but concise
- Don't include quotes
- Focus on the main topic or intent

Title:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        generated_name = response.content.strip()
        
        # Fallback to truncated message if generation fails
        if not generated_name or len(generated_name) > 30:
            generated_name = first_message[:27] + "..." if len(first_message) > 27 else first_message
            
        return generated_name
        
    except Exception as e:
        print(f"Error generating chat name: {e}")
        # Fallback to truncated first message
        return first_message[:27] + "..." if len(first_message) > 27 else first_message

def chat_node(state: ChatState):
    messages = state['messages']
    current_chat_name = state.get('chat_name', 'Untitled Chat')
    
    # Check if this is the first user message and we need to generate a chat name
    user_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    
    # If this is the first user message and chat name is still default, generate a new name
    if (len(user_messages) == 1 and 
        current_chat_name in ['Untitled Chat', 'New Chat', None]):
        
        first_message = user_messages[0].content
        new_chat_name = generate_chat_name(first_message)
        print(f"Generated chat name: '{new_chat_name}' from message: '{first_message[:50]}...'")
    else:
        new_chat_name = current_chat_name
    
    # Generate the AI response
    response = llm.invoke(messages)
    
    return {
        "messages": [response],
        "chat_name": new_chat_name
    }

# Rest of your backend code remains the same
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    """Retrieve all threads with their chat names from graph state"""
    all_threads = {}
    
    thread_ids = set()
    for checkpoint in checkpointer.list(None):
        cfg = checkpoint.config.get('configurable', {})
        tid = cfg.get('thread_id')
        if tid:
            thread_ids.add(tid)
    
    for thread_id in thread_ids:
        try:
            state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
            chat_name = state.values.get('chat_name', 'Untitled Chat')
            all_threads[thread_id] = chat_name
            
        except Exception as e:
            print(f"Error retrieving state for thread {thread_id}: {e}")
            all_threads[thread_id] = 'Untitled Chat'
    
    return [{"id": tid, "name": all_threads[tid]} for tid in all_threads]





















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
#         "chat_name": chat_name  # This will be persisted in the graph state
#     }

# conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# # Checkpointer
# checkpointer = SqliteSaver(conn=conn)

# graph = StateGraph(ChatState)
# graph.add_node("chat_node", chat_node)
# graph.add_edge(START, "chat_node")
# graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# def retrieve_all_threads():
#     """
#     The correct way to get thread data with chat names from graph state
#     """
#     all_threads = {}
    
#     # Get all unique thread_ids first
#     thread_ids = set()
#     for checkpoint in checkpointer.list(None):
#         cfg = checkpoint.config.get('configurable', {})
#         tid = cfg.get('thread_id')
#         if tid:
#             thread_ids.add(tid)
    
#     # Now get the actual state for each thread
#     for thread_id in thread_ids:
#         try:
#             # Get the current state for this thread
#             state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
            
#             # Extract chat_name from the state values
#             chat_name = state.values.get('chat_name', 'Untitled Chat')
#             all_threads[thread_id] = chat_name
            
#             print(f"Retrieved: thread_id={thread_id}, chat_name={chat_name}")
            
#         except Exception as e:
#             print(f"Error retrieving state for thread {thread_id}: {e}")
#             all_threads[thread_id] = 'Untitled Chat'
    
#     return [{"id": tid, "name": all_threads[tid]} for tid in all_threads]

# # Alternative approach: Direct database query (if you want to see what's actually stored)
# def debug_checkpoint_structure():
#     """
#     Debug function to see what's actually stored in checkpoints
#     """
#     print("=== DEBUG: Checkpoint Structure ===")
#     for i, checkpoint in enumerate(checkpointer.list(None)):
#         if i > 2:  # Only show first 3 for debugging
#             break
#         print(f"Checkpoint {i}:")
#         print(f"  Config: {checkpoint.config}")
#         print(f"  Values: {checkpoint.values}")
#         print(f"  Has values attr: {hasattr(checkpoint, 'values')}")
#         if hasattr(checkpoint, 'values') and checkpoint.values:
#             print(f"  Values keys: {checkpoint.values.keys() if checkpoint.values else 'None'}")
#         print("---")