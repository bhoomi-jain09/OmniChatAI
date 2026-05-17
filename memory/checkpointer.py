import os
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

# Ensure the data directory exists before connecting
os.makedirs("data", exist_ok=True)

conn = sqlite3.connect("data/chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
