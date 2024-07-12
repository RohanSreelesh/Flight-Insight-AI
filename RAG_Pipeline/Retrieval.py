import os
from typing import List, Dict
from pinecone import Pinecone
import google.generativeai as genai
from RAG_Pipeline.constants import SUPPORTED_AIRLINES, TRAVELLER_TYPES, SEAT_TYPES
import json
from typing import Tuple
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Constants
INDEX_NAME = "airline-reviews"
TOP_K = os.getenv("TOP_K")

# Init
embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

import json

#Convert the query string into a vector embedding.
def embed_query(query: str) -> List[float]:
    return embedding_model.encode([query])[0].tolist()

#Extract structured information from the query.
def extract_query_parameters(query: str) -> Dict:
    prompt = f"""
    Extract structured information from this airline review query: "{query}"
    
    Please extract the following information if present:
    - airline (must be one of: {', '.join(SUPPORTED_AIRLINES)})
    - traveller_type (must be one of: {', '.join(TRAVELLER_TYPES)})
    - seat_type (must be one of: {', '.join(SEAT_TYPES)})
    - route (origin and destination)
    - aspect (specific aspect of interest, e.g., food, service, comfort)

    Return the information in JSON format. Use exactly the keys mentioned above.
    If a piece of information is not present or doesn't match the provided options, omit that field.
    """

    response = model.generate_content(prompt)
    
    # Clean the response text
    clean_response = response.text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response.split("```json")[1]
    if clean_response.endswith("```"):
        clean_response = clean_response.rsplit("```", 1)[0]
    
    # Parse the JSON response
    try:
        extracted_info = json.loads(clean_response)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON. Raw response: {clean_response}")
        extracted_info = {}
    
    return extracted_info

#Validate and filter the extracted parameters.
def validate_and_filter_parameters(extracted_params: Dict) -> Dict:
    filter_params = {}
    
    if 'airline' in extracted_params and extracted_params['airline'] in SUPPORTED_AIRLINES:
        filter_params['airline'] = extracted_params['airline']
    
    # if 'traveller_type' in extracted_params and extracted_params['traveller_type'] in TRAVELLER_TYPES:
    #     filter_params['Type Of Traveller'] = extracted_params['traveller_type']
    
    # if 'seat_type' in extracted_params and extracted_params['seat_type'] in SEAT_TYPES:
    #     filter_params['Seat Type'] = extracted_params['seat_type']
    
    return filter_params

#list dict is just the reviews and the second dict is the extracted parameters
def retrieve_relevant_reviews(query: str) -> Tuple[List[Dict], Dict]:
    """
    Retrieve the most relevant reviews based on the query.
    """
    # Extract parameters using Gemini Flash
    extracted_params = extract_query_parameters(query)
    print("Extracted parameters:", extracted_params)
    
    filter_params = validate_and_filter_parameters(extracted_params)
    print("Validated filter parameters:", filter_params)
    
    if not filter_params:
        print("No valid filter parameters found. Returning empty results.")
        return [], extracted_params
    
    # Convert query to vector embedding
    query_vector = embed_query(query)
    
    # Query Pinecone
    try:
        results = index.query(
            vector=query_vector,
            top_k=TOP_K,
            include_metadata=True,
            filter=filter_params
        )
    except Exception as e:
        print(f"Error querying Pinecone: {e}")
        return [], extracted_params
    
    # Process and return results
    relevant_reviews = []
    for match in results['matches']:
        relevant_reviews.append({
            'id': match['id'],
            'score': match['score'],
            'metadata': match['metadata']
        })
    
    return relevant_reviews, extracted_params

# Example usage for testing but will be used mainly by our api
if __name__ == "__main__":
    query = "What do people think about the food on British Airways business class flights for solo leisure travelers?"
    reviews, params = retrieve_relevant_reviews(query)
    print("\nExtracted Parameters:", params)
    print("\nRelevant Reviews:")
    for review in reviews:
        print(f"ID: {review['id']}, Score: {review['score']}")
        print(f"Metadata: {review['metadata']}")
        print("---")