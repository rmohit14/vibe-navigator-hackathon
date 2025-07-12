import os
import json
from dotenv import load_dotenv
import pymongo
import certifi
from langchain_core.documents import Document
# --- [START]  CHANGES ARE HERE ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# --- [END]  CHANGES ARE HERE ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MONGO_URI or not GOOGLE_API_KEY:
    raise ValueError("MONGO_URI and GOOGLE_API_KEY must be set in the .env file")

client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database("vibe_navigator_db")
reviews_collection = db.get_collection("reviews")

# --- [START] THIS SECTION IS CHANGED ---
# Use Google's lightweight embedding model instead of HuggingFace's
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.2)
# --- [END] THIS SECTION IS CHANGED ---

def build_vector_store():
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

    print("Creating embeddings with the Google API. This may take a moment...")
    # Note: This will now use your Google API key and may incur small costs if you build many times.
    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("Vector store created and persisted.")
    return vector_store

def get_vibe_summary(location_name: str) -> dict:
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
        context = "\n---\n".join([doc.page_content for doc in truly_relevant_docs])
        template = """
        You are Vibe Navigator, an insightful and witty AI city guide...
        """ # Prompt is unchanged
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
    else:
        all_known_locations = reviews_collection.distinct("location_name")
        return {
            "status": "not_found",
            "message": f"I couldn't find specific reviews for '{location_name}'.",
            "suggestions": all_known_locations
        }

if __name__ == '__main__':
    build_vector_store()