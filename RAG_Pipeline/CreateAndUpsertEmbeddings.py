import os
import pandas as pd
from tqdm.auto import tqdm
from typing import List, Dict
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Pinecone setup
pinecone = Pinecone(api_key=PINECONE_API_KEY)

# SentenceTransformer setup
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

# Constants
INDEX_NAME = "airline-reviews"
BATCH_SIZE = 100
VECTOR_DIMENSION = 384  

#create pinecone index if does not exist
def create_pinecone_index(index_name: str, dimension: int):
    if index_name not in pinecone.list_indexes().names():
        pinecone.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Created new index: {index_name}")
    else:
        print(f"Index {index_name} already exists")

#process metadata for a given row
def prepare_metadata(row: pd.Series) -> Dict:
    return {
        "row_id": int(row.name),
        "airline": row["airline"],
        "rating": float(row["overall_rating"]),
        "date": row["Date Flown"],
        "route": row["Route"],
        "traveler_type": row["Type Of Traveller"],
        "cabin_class": row["Seat Type"],
        "review_text": row["review_text"]
    }

#Upload vectors in batches to pinecone cloud
def upsert_to_pinecone(index, ids: List[str], vectors: List[List[float]], metadatas: List[Dict]):
    """Upsert a batch of vectors to Pinecone."""
    try:
        index.upsert(vectors=zip(ids, vectors, metadatas))
    except Exception as e:
        print(f"Error upserting to Pinecone: {e}")

def main():
    # Load the cleaned data
    df = pd.read_csv("Data/all_airlines_reviews_cleaned.csv")
    print(f"Loaded {len(df)} reviews")

    # Create Pinecone index
    create_pinecone_index(INDEX_NAME, dimension=VECTOR_DIMENSION)
    index = pinecone.Index(INDEX_NAME)

    for i in tqdm(range(0, len(df), BATCH_SIZE), desc="Processing batches"):
        batch = df.iloc[i:i+BATCH_SIZE]
        
        # Prepare data
        ids = batch.index.astype(str).tolist()
        texts = batch["review_text"].tolist()
        metadatas = [prepare_metadata(row) for _, row in batch.iterrows()]
        
        # Create embeddings
        try:
            vectors = model.encode(texts).tolist()
        except Exception as e:
            print(f"Error creating embeddings for batch starting at index {i}: {e}")
            continue
        
        # Upsert to Pinecone
        upsert_to_pinecone(index, ids, vectors, metadatas)

    print("Embedding and upserting process completed")

if __name__ == "__main__":
    main()