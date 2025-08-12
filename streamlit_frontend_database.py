import streamlit as st
from langgraph_database_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = str(uuid.uuid4())  # Convert to string for consistency
    return thread_id

def reset_chat():
    # Only create a new chat if the current one has messages
    current_messages = st.session_state.get('message_history', [])

    if current_messages:
        thread_id = generate_thread_id()
        st.session_state['thread_id'] = thread_id
        add_thread(thread_id) # Defaults to "Untitled Chat"
        st.session_state['message_history'] = []
        st.session_state['chat_name'] = "Untitled Chat"  # Reset chat name
    else:
        # If current chat is empty, just reset messages without creating new thread
        st.session_state['message_history'] = []

def add_thread(thread_id, name="Untitled Chat"):
    if not any(thread["id"] == thread_id for thread in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({"id": thread_id, "name": name})
        st.session_state['chat_name'] = name

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    chat_name = state.values.get('chat_name', 'Untitled Chat')
    return messages, chat_name

# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_name' not in st.session_state:  # Initialize chat_name
    st.session_state['chat_name'] = "Untitled Chat"

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])

# **************************************** Sidebar UI *********************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat', key="btn_new_chat"):
    reset_chat()

st.sidebar.header('My Conversations')

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread['name'], key=f"thread_button_{thread['id']}"):
        st.session_state['thread_id'] = thread['id']
        st.session_state['chat_name'] = thread['name']  # Set the chat name when switching
        messages, chat_name = load_conversation(thread['id'])
        
        # Update chat name from stored state if available
        if chat_name and chat_name != 'Untitled Chat':
            st.session_state['chat_name'] = chat_name
            # Update the thread name in session if it's different
            for t in st.session_state['chat_threads']:
                if t['id'] == thread['id']:
                    t['name'] = chat_name
                    break

        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# **************************************** Main UI ************************************

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # If first message in a thread, use it as the name
    for thread in st.session_state['chat_threads']:
        if thread['id'] == st.session_state['thread_id'] and thread['name'] in ["New Chat", "Untitled Chat"]:
            new_name = user_input[:30] + ("..." if len(user_input) > 30 else "")
            thread['name'] = new_name
            st.session_state['chat_name'] = new_name
            print(f"Updated chat name: {new_name}")

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {
        'thread_id': st.session_state['thread_id'],
        'chat_name': st.session_state['chat_name']  # Ensure this is properly set
        }
    }
    
    print(f"Sending CONFIG: {CONFIG}")  # Debug print

    # Generate response with proper chat_name in initial state
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {
                    'messages': [HumanMessage(content=user_input)],
                    'chat_name': st.session_state['chat_name']  # Include chat_name in initial state
                },
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})






















# import streamlit as st
# from langgraph_database_backend import chatbot, retrieve_all_threads
# from langchain_core.messages import HumanMessage
# import uuid

# # **************************************** utility functions *************************

# def generate_thread_id():
#     thread_id = str(uuid.uuid4())
#     return thread_id

# def reset_chat():
#     # Only create a new chat if the current one has messages
#     current_messages = st.session_state.get('message_history', [])

#     if current_messages:
#       thread_id = generate_thread_id()
#       st.session_state['thread_id'] = thread_id
#       add_thread(thread_id) # Defaults to "Untitled Chat"
#       st.session_state['message_history'] = []
#       st.session_state['chat_name'] = "Untitled Chat"
#     else:
#         # If current chat is empty, just reset messages without creating new thread
#         st.session_state['message_history'] = []

# def add_thread(thread_id, name="Untitled Chat"):
#     if not any(thread["id"] == thread_id for thread in st.session_state['chat_threads']):
#         st.session_state['chat_threads'].append({"id": thread_id, "name": name})
#         st.session_state['chat_name'] = name

# def load_conversation(thread_id):
#     state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
#     messages = state.values.get('messages', [])
#     chat_name = state.values.get('chat_name', 'Untitled Chat')
#     return state.values.get('messages', [])


# # **************************************** Session Setup ******************************
# if 'message_history' not in st.session_state:
#     st.session_state['message_history'] = []

# if 'thread_id' not in st.session_state:
#     st.session_state['thread_id'] = generate_thread_id()

# if 'chat_name' not in st.session_state:  # Initialize chat_name
#     st.session_state['chat_name'] = "Untitled Chat"

# if 'chat_threads' not in st.session_state:
#     st.session_state['chat_threads'] = retrieve_all_threads()

# add_thread(st.session_state['thread_id'])


# # **************************************** Sidebar UI *********************************

# st.sidebar.title('LangGraph Chatbot')

# if st.sidebar.button('New Chat', key="btn_new_chat"):
#     reset_chat()

# st.sidebar.header('My Conversations')

# for thread in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(thread['name'], key=f"thread_button_{thread['id']}"):
#         st.session_state['thread_id'] = thread['id']
#         st.session_state['chat_name'] = thread['name']
#         messages = load_conversation(thread['id'])

#         temp_messages = []

#         for msg in messages:
#             if isinstance(msg, HumanMessage):
#                 role='user'
#             else:
#                 role='assistant'
#             temp_messages.append({'role': role, 'content': msg.content})

#         st.session_state['message_history'] = temp_messages


# # **************************************** Main UI ************************************

# # loading the conversation history
# for message in st.session_state['message_history']:
#     with st.chat_message(message['role']):
#         st.text(message['content'])

# user_input = st.chat_input('Type here')

# if user_input:

#     # If first message in a thread, use it as the name
#     for thread in st.session_state['chat_threads']:
#         if thread['id'] == st.session_state['thread_id'] and thread['name'] in ["New Chat", "Untitled Chat"]:
#             new_name = user_input[:30] + ("..." if len(user_input) > 30 else "")
#             thread['name'] = new_name
#             st.session_state['chat_name'] = new_name
#             print(f"Updated chat name: {new_name}")

#     # first add the message to message_history
#     st.session_state['message_history'].append({'role': 'user', 'content': user_input})
#     with st.chat_message('user'):
#         st.text(user_input)

#     CONFIG = {'configurable': {
#         'thread_id': st.session_state['thread_id'],
#         # 'chat_name': st.session_state.get('chat_name', '')
#         'chat_name': st.session_state['chat_name']
#         }
#     }

#     print(f"Sending CONFIG: {CONFIG}")  # Debug print

#     # first add the message to message_history
#     with st.chat_message('assistant'):

#         ai_message = st.write_stream(
#             message_chunk.content for message_chunk, metadata in chatbot.stream(
#                 {
#                     'messages': [HumanMessage(content=user_input)],
#                     'chat_name': st.session_state['chat_name']
#                 },
#                 config= CONFIG,
#                 stream_mode= 'messages'
#             )
#         )

#     st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})