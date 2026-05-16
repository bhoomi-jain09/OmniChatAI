import streamlit as st
from langraph_backebd import workflow,retrieve_all_thread
from langchain_core.messages import HumanMessage 
import uuid


#*******************************************utility function*******************************************

def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id
def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]
def add_thread(thread_id):
    if thread_id not in st.session_state["chat_thread"]:
        st.session_state['chat_thread'].append(thread_id)
def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    if not state or not hasattr(state,"values"):
        return[]
    return state.values.get('message', [])

#******************************sessionstate*********************************
#session_state-->dict it not erase data if until you refresh the whole page
if "message_history" not in st.session_state:
    st.session_state["message_history"]=[]
if "thread_id" not in st.session_state:
    st.session_state["thread_id"]=generate_thread_id()
if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"]=retrieve_all_thread()
add_thread(st.session_state["thread_id"])

#*********************************slidebar UI************************************************************************
st.sidebar.title("OmniChat Ai")
if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for thread_id in st.session_state["chat_thread"][::]:
    if st.sidebar.button(str(thread_id)):
        st.session_state["thread_id"]=thread_id
        messages=load_conversation(thread_id)
        #now problem is langgraph return in list format but we have output in dict format{'role':'user','content':
        # 'content'} for convert into this format
        temp_messages=[]
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role':role,'content':msg.content})
        st.session_state["message_history"]=temp_messages

#******************************main ui*************************************************

#loading the conversatation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
user_input=st.chat_input('type here')
if user_input:
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    #CONFIG={'configurable':{'thread_id':st.session_state["thread_id"]}}
    CONFIG={
        "configurable":{'thread_id':st.session_state['thread_id']},
        "metadata":{"thread_id":st.session_state['thread_id']},
        "runname":"chat-turn",
    }
    #streaming
    with st.chat_message('assistant'):
        ai_message=st.write_stream(
            message_chunk.content for message_chunk,metadata in workflow.stream(
                {'message':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})

