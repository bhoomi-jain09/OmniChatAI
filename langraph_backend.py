from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage
from langgraph.graph.message import add_messages
#from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Any, Dict, Optional, TypedDict,Annotated
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import sqlite3 
import requests
import tempfile
import os
load_dotenv()
model=ChatGroq(model="llama-3.3-70b-versatile",temperature=0)
embeddings = HuggingFaceEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None
def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.

    Returns a summary dict that can be surfaced in the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        _THREAD_METADATA[str(thread_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        # The FAISS store keeps copies of the text, so the temp file is safe to remove.
        try:
            os.remove(temp_path)
        except OSError:
            pass
#tools
search_tool=DuckDuckGoSearchRun(region="us-eng")

@tool
def calculator(first_num:float,second_num:float,operation:str):
     """ tool for the calculation like addition,subtraction,division and multipication"""
     try:
          if operation=="addition":
               result=first_num+second_num
          elif operation=="subtraction":
               result=first_num-second_num
          elif operation=="Multipication":
               result=first_num*second_num
          elif operation=="division":
               if second_num ==0:
                    print("error denominator can not zero")
               result=first_num/second_num
          else:
               print("please enter valid number for operation")
          return {
               first_num:first_num,
               second_num:second_num,
               operation:operation,
               result:result
          }
     except Exception as e:
          return ("error",str(e))

@tool
def stock_price(symbol:str):
        """
        Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
        using Alpha Vantage with API key in the URL.
        """
        url = (
            "https://www.alphavantage.co/query"f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey=AIXAHRQNKU26V9P3"
        )
        r = requests.get(url)
        return r.json()

@tool
def rag(query:str,thread_id:Optional[str]=None)-> dict:
               """ Retrive relevent information Retrieve relevant information from the uploaded PDF for this chat thread.
          Always include the thread_id when calling this tool.
          """
               retriever= _get_retriever(thread_id)
               if retriever is None:
                    return {
                    "error": "No document indexed for this chat. Upload a PDF first.",
                    "query": query,
               }

               result = retriever.invoke(query)
               context = [doc.page_content for doc in result]
               metadata = [doc.metadata for doc in result]

               return {
                    "query": query,
                    "context": context,
                    "metadata": metadata,
                    "source_file": _THREAD_METADATA.get(str(thread_id), {}).get("filename"),
               }


tools =( [search_tool, stock_price, calculator, rag])
llm_with_tools = model.bind_tools(tools)



class chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chatnode(state: chatstate,config=None):
    """ LLM that may answer or request a tool call"""
    thread_id = None
    if config and isinstance(config, dict):
        thread_id = config.get("configurable", {}).get("thread_id")

    system_message = SystemMessage(
        content=(
            "You are a helpful assistant. For questions about the uploaded PDF, call "
            "the `rag_tool` and include the thread_id "
            f"`{thread_id}`. You can also use the web search, stock price, and "
            "calculator tools when helpful. If no document is available, ask the user "
            "to upload a PDF."
        )
    )

    messages = [system_message, *state["messages"]]
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}
tool_node=ToolNode(tools)
conn=sqlite3.connect("chatbot_db",check_same_thread=False)#checsame thread not check the thread_id 

checkpointer=SqliteSaver(conn=conn)
#checkpointer=InMemorySaver()
graph=StateGraph(chatstate)
graph.add_node("chatnode",chatnode)
graph.add_node("tools",tool_node)
graph.add_edge(START,"chatnode")
graph.add_conditional_edges("chatnode",tools_condition)
graph.add_edge("tools","chatnode")
workflow=graph.compile(checkpointer=checkpointer)
def retrieve_all_thread():
    all_thread=set()
    for checkpoint in checkpointer.list(None):
            all_thread.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread)

def thread_has_document(thread_id: str) -> bool:
    return str(thread_id) in _THREAD_RETRIEVERS


def thread_document_metadata(thread_id: str) -> dict:
    return _THREAD_METADATA.get(str(thread_id), {})