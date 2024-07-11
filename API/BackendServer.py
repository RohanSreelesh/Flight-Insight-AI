import os
import logging
from typing import List, Dict
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from RAG_Pipeline.Retrieval import retrieve_relevant_reviews 
from RAG_Pipeline.constants import SUPPORTED_AIRLINES 
import asyncio 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_prompt(query: str, reviews: List[Dict]) -> str:
    if not reviews:
        airlines_list = ", ".join(SUPPORTED_AIRLINES)
        return f"""You are an AI assistant specialized in providing insights about airline reviews. 
        Unfortunately, no relevant reviews were found for the following query: "{query}"
        Please inform the user that either they did not specify a supported airline or the airline they mentioned is not currently supported. 
        Apologize for the inconvenience and ask them to try again with a query that includes one of the following supported airlines: {airlines_list}.
        Encourage the user to be specific about which airline they are inquiring about in their next query."""

    system_prompt = """You are an AI assistant specialized in providing insights about airline reviews. 
    Use the provided reviews to answer the user's query. Be informative and base your answers on the reviews. 
    If the reviews don't contain relevant information to answer the query, say so. Be verbose and provide detailed responses."""

    review_text = "\n".join([f"Review {i+1}: {review['metadata']['review_text']}" for i, review in enumerate(reviews[:5])])

    full_prompt = f"{system_prompt}\n\nRelevant Reviews:\n{review_text}\n\nUser Query: {query}\n\nResponse:"
    return full_prompt

async def stream_response(websocket: WebSocket, response):
    complete_response = ""
    async for chunk in response:
        if chunk.text:
            complete_response += chunk.text
            await websocket.send_text(chunk.text)
            #await asyncio.sleep(0.01)
    return complete_response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            query = await websocket.receive_text()
            logger.info(f"Received query: {query}")
            
            # Retrieve relevant reviews
            reviews, _ = retrieve_relevant_reviews(query)
            logger.info(f"Retrieved reviews: {reviews}")
            
            # Create the full prompt
            full_prompt = create_prompt(query, reviews)
            logger.info(f"Full prompt: {full_prompt}")
            
            # Generate streaming response
            response = await model.generate_content_async(full_prompt, stream=True)
            
            # Stream the response
            complete_response = await stream_response(websocket, response)
            
            # Log the complete response
            logger.info(f"Complete response: {complete_response}")
            
            # Send a message to indicate the end of the response
            await websocket.send_text("[END_OF_RESPONSE]")
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
        await websocket.send_text("Something went wrong please try again.")
        await websocket.send_text("[END_OF_ERROR_RESPONSE]")
        await websocket.close()

@app.get("/supported-airlines")
def get_supported_airlines():
    return {"airlines": SUPPORTED_AIRLINES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)