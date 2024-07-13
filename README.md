# Flight-Insight-AI
## Introduction
Flight Insight AI is a chatbot system designed to provide intelligent insights and analysis of airline reviews. Using natural language processing and machine learning techniques, Flight Insight AI offers users a seamless interface to query and understand airline experiences based on real customer reviews. Try it [Here](https://flight-insight-ai.vercel.app/)!

## System Architecture
![mermaid-diagram-2024-07-13-120412](https://github.com/user-attachments/assets/c3aa582d-6ab0-48b9-9323-aa083435d192)

- Frontend: A React application providing a responsive and interactive user interface.
- Backend: A FastAPI server that handles real-time communication and orchestrates the AI components.
- Vector Database: Pinecone is used for efficient similarity search of review embeddings.
- Language Model: Google's Gemini Flash for natural language understanding and generation.
- Data Processing: Several scripts to get and clean the data.

### Sequence Diagram
![mermaid-diagram-2024-07-13-011140](https://github.com/user-attachments/assets/2dc5218d-cc9c-40dd-a190-a3a1d56079f0)

1. User Input: The user types the query into the Frontend interface. 
  - Query Transmission: The Frontend sends this query to the FastAPI Backend via a WebSocket connection.

2. Airline Extraction:
  - The Gemini Flash model for airline extraction identifies the airline in question.

3. Query Embedding:
  - The processed query is sent to the Query Embedder. The Query Embedder converts the text query into a vector embedding, similar to how the reviews were embedded.

4. Relevant Review Retrieval:
  - The Retriever takes this query embedding and searches the Pinecone Vector DB for similar review embeddings. It retrieves the TOP_K relevant reviews similar to the user query.

5. Prompt Generation:

  - The Prompt Generator receives:
    - The original query
    - The relevant reviews from the Retriever

  - It combines this information into a structured prompt for the language model.


6. Response Generation:

- The generated prompt is sent to the Gemini Flash model for response generation. This model processes the prompt and generates a comprehensive response based on the relevant reviews.


7. Response Delivery:

- The generated response is sent back to the Frontend via the WebSocket connection. The Frontend streams this response to the user.

## Features
- Output Streaming: Utilizes WebSocket for streaming AI responses, providing a dynamic and engaging user experience.
- Intelligent Review Analysis: Leverages a RAG (Retrieval-Augmented Generation) system to provide insights based on relevant customer reviews.
- Dynamic Airline Information: Automatically detects airline mentioned and responds based on that.
- Vector Search: Pinecone DB is used for efficient similarity search of review embeddings, ensuring fast and relevant retrievals.
- LLM: Integrates Google's Gemini Flash for high-quality natural language processing and generation.

## Technology Stack

- Frontend: React, Tailwind CSS
- Backend: FastAPI
- Vector Database: Pinecone
- Language Model: Google Gemini Flash
- Embedding Model: SentenceTransformer
- Deployment: Vercel, Render (https://flight-insight-ai.vercel.app/)

