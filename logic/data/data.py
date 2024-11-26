import pandas as pd
import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

print(f"Current working directory: {os.getcwd()}")

# Define the absolute path to the CSV file
current_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Current directory: {current_dir}")

file_path = os.path.join(current_dir, "customer_leads_agent_qa_data_csv.csv")

qa_dataset = pd.read_csv(file_path, delimiter=",", encoding="latin1").to_dict(
    orient="records"
)

# Convert questions into embeddings
embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    model="embed-english-light-v3.0",
)

questions = [item["prompt_text"] for item in qa_dataset]
vector_store = FAISS.from_texts(questions, embeddings)

# Map each vector to its expected response
responses = {item["prompt_text"]: item["expected_response"] for item in qa_dataset}
