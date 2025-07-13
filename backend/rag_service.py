import os
import json
from dotenv import load_dotenv
import pymongo
import certifi
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
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

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.2)

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

    print("Creating embeddings with the Google API...")
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

    # Use a broad search and then filter in Python for reliability
    retriever = vector_store.as_retriever(search_kwargs={"k": 50})
    all_retrieved_docs = retriever.invoke(location_name)

    truly_relevant_docs = []
    if all_retrieved_docs:
        for doc in all_retrieved_docs:
            if location_name.lower() in doc.metadata.get("location_name", "").lower():
                truly_relevant_docs.append(doc)

    if truly_relevant_docs:
        context = "\n---\n".join([doc.page_content for doc in truly_relevant_docs])
        template = """
        You are Vibe Navigator, an insightful and witty AI city guide. Your task is to generate a detailed "vibe report" for a location based *only* on the user reviews provided in the CONTEXT.
        Your response MUST be a single, valid JSON object with the following keys: "summary", "vibe_dimensions", "tags", and "emojis".
        - "summary": (string) Your 2-3 sentence summary.
        - "vibe_dimensions": (object) An object with "ambience", "crowd", and "noise_level" as keys.
        - "tags": (array of strings) 5 relevant, single-word, lowercase vibe tags.
        - "emojis": (array of strings) 4-5 emojis that represent the vibe.
        CONTEXT:
        {context}
        QUESTION:
        What is the vibe of {question}?
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        response_str = chain.invoke({"context": context, "question": location_name}).content

        try:
            json_start = response_str.find('{')
            json_end = response_str.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = response_str[json_start:json_end]
                vibe_json = json.loads(json_str)
                vibe_json['status'] = 'found'
                vibe_json['citations'] = [doc.page_content for doc in truly_relevant_docs]
                return vibe_json
            else:
                raise json.JSONDecodeError("No JSON object found in response", response_str, 0)
        except json.JSONDecodeError:
            return {"error": "Failed to parse the vibe summary from the AI."}
    else:
        return {"status": "not_found", "message": f"Could not find reviews for '{location_name}'."}

def get_locations_by_vibe(vibe_tag: str) -> list[str]:
    vibe_collection = db.get_collection("location_vibes")
    matching_locations = vibe_collection.find(
        {"tags": {"$regex": f"^{vibe_tag}$", "$options": "i"}}
    )
    location_names = [doc.get("location_name") for doc in matching_locations]
    return sorted(list(filter(None, location_names)))

if __name__ == '__main__':
    build_vector_store()