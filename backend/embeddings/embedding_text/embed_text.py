from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
PINECONE_API_KEY = os.getenv("Pinecone_API_KEY")
pc = Pinecone(api_key="PINECONE_API_KEY")