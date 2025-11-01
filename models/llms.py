from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
"""
# Load environment variables
load_dotenv()
try:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
except:
    raise ValueError("GROQ_API_KEY not found in environment variables.")
"""

if st.secrets["GROQ_API_KEY"] is None:
    raise ValueError("GROQ_API_KEY variable is not streamlit.secrets.toml")

api_key = st.secrets["GROQ_API_KEY"]

def create_llm(temperature:float=0.3):
    """
    Create and return a ChatGroq LLM instance with the specified temperature.
        Args:
            temperature (float): The temperature setting for the LLM.
        Returns:
        ChatGroq: An instance of the ChatGroq LLM.
    """
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=GROQ_API_KEY
    )
