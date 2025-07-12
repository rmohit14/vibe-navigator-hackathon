# backend/rag_service.py
import os
import json
from dotenv import load_dotenv
import pymongo
import certifi
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# --- Database and API Setup ---
MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MONGO_URI or not GOOGLE_API_KEY:
    raise ValueError("MONGO_URI and GOOGLE_API_KEY must be set in the .env file")

client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database("vibe_navigator_db")
reviews_collection = db.get_collection("reviews")

# Initialize models
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2) # Slightly more creative temp
# --- End Setup ---

def build_vector_store():
    """
    Builds a Chroma vector store from reviews in MongoDB.
    This function creates Document objects with metadata for robust retrieval.
    """
    print("Fetching reviews from MongoDB...")
    reviews = list(reviews_collection.find({}))
    if not reviews:
        print("No reviews found in the database.")
        return None

    documents = []
    for review in reviews:
        if 'review' in review and review['review']:
            metadata = {"location_name": review.get("location_name", "Unknown")}
            doc = Document(page_content=review['review'], metadata=metadata)
            documents.append(doc)
    
    if not documents:
        print("No review text found in the fetched documents.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    print("Creating embeddings with the local model. This may take a moment...")
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Vector store created and persisted.")
    return vector_store

# In backend/rag_service.py, replace the get_vibe_summary function

def get_vibe_summary(location_name: str) -> dict:
    """
    Retrieves and summarizes the vibe for a location using a robust RAG pipeline.
    """
    try:
        vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
    except Exception as e:
        return {"error": f"Could not load vector store. Have you run the indexing? Error: {e}"}

    retriever = vector_store.as_retriever(search_kwargs={"k": 10})
    all_retrieved_docs = retriever.invoke(location_name)

    truly_relevant_docs = []
    if all_retrieved_docs:
        for doc in all_retrieved_docs:
            if location_name.lower() in doc.metadata.get("location_name", "").lower():
                truly_relevant_docs.append(doc)

    if truly_relevant_docs:
        print(f"Found {len(truly_relevant_docs)} relevant docs for: {location_name}")
        context = "\n---\n".join([doc.page_content for doc in truly_relevant_docs])
        
        template = """
        You are Vibe Navigator, an insightful and witty AI city guide. Your task is to generate a detailed "vibe report" for a location based *only* on the user reviews provided in the CONTEXT.

        Follow these steps:
        1.  Analyze the Vibe: Read all reviews in the CONTEXT to understand the overall atmosphere.
        2.  Identify Key Dimensions: Based on the reviews, analyze the following dimensions:
            - Ambience: What is the general feeling? (e.g., "cozy and rustic", "modern and bustling", "peaceful and serene").
            - Crowd: Who goes there? (e.g., "popular with students", "a mix of families and young professionals", "mostly tourists").
            - Noise Level: Is it loud or quiet? (e.g., "lively with upbeat music", "generally quiet and good for conversation").
        3.  Synthesize a Summary: Write a playful but insightful 2-3 sentence summary. Acknowledge both positive and negative points if they exist (e.g., "it can get a bit loud, but the energy is infectious").
        4.  Extract Tags & Emojis: Generate relevant tags and emojis that capture the essence of the vibe.

        CONTEXT:
        {context}

        QUESTION:
        What is the vibe of {question}?

        Your response MUST be a single, valid JSON object with the following keys: "summary", "vibe_dimensions", "tags", and "emojis".
        - "summary": (string) Your 2-3 sentence summary.
        - "vibe_dimensions": (object) An object with "ambience", "crowd", and "noise_level" as keys.
        - "tags": (array of strings) 5 relevant, single-word, lowercase vibe tags.
        - "emojis": (array of strings) 4-5 emojis that represent the vibe.
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        response_str = chain.invoke({"context": context, "question": location_name}).content
        
        try:
            if response_str.strip().startswith("```json"):
                response_str = response_str.strip()[7:-3]
            vibe_json = json.loads(response_str)
            vibe_json['status'] = 'found'
            vibe_json['citations'] = [doc.page_content for doc in truly_relevant_docs]
            return vibe_json
        except json.JSONDecodeError:
            return {"error": "Failed to parse the vibe summary from the AI.", "raw_response": response_str}

    # --- THIS IS THE FINAL, IMPROVED LOGIC FOR SUGGESTIONS ---
    else:
        print(f"No direct context found for: {location_name}. Acting as helpful librarian.")
        # Get all unique location names directly from the main database
        all_known_locations = reviews_collection.distinct("location_name")

        return {
            "status": "not_found",
            "message": f"I couldn't find specific reviews for '{location_name}'.",
            "suggestions": all_known_locations # This is now a complete list
        }

if __name__ == '__main__':
    build_vector_store()