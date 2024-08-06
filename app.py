from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone,ServerlessSpec
import numpy as np

from cryptography.fernet import Fernet

with open('encryption_key.key', 'rb') as key_file:
    encryption_key = key_file.read()

cipher_suite = Fernet(encryption_key)

# Load the encrypted API key
with open('encrypted_api_key.key', 'rb') as encrypted_file:
    encrypted_api_key = encrypted_file.read()

# Decrypt the API key
decrypted_api_key = cipher_suite.decrypt(encrypted_api_key).decode()

PINECONE_API_KEY = 'f8dca2e6-17b3-4d2d-bf68-1a09df19b2d4'

# Initialize OpenAI and Pinecone
client=OpenAI(api_key=decrypted_api_key)
pine=Pinecone(api_key=PINECONE_API_KEY, environment='us-west1-gcp')
# Create and connect to Pinecone index
index_name_1 = 'text-classification'
dimension = 3072  # Dimension should match OpenAI's embedding size
index_1 = pine.Index(index_name_1)
index_name_2 = 'job-listings'
dimension = 3072  # Dimension should match OpenAI's embedding size
index_2 = pine.Index(index_name_2)
index_name_3 = "help-listings"
index_3 = pine.Index(index_name_3)

app = FastAPI()
def text_generate(question,primer):
    primer="you are a Bangla chatbot who assist about getting job"+primer+"this is the data and you have to answer depending on this data but always try to answer in short"
    response=client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": question},
            ],
            max_tokens=100,
            stream=False,
        )
    return response
def classify_text(text):
    # Embed the input text
    input_embedding = client.embeddings.create(input=text, model='text-embedding-3-large').data[0].embedding
    
    # Query Pinecone
    result = index_1.query(vector=[input_embedding], top_k=5)
    print(result)
    
    if not result['matches']:
        return "No category found"
    
    # Retrieve the closest category
    closest_category = result['matches'][0]['id']
    if closest_category=="Sr_job":
        job_result = index_2.query(vector=[input_embedding], top_k=1,include_values=True,
        include_metadata=True)
        p=job_result['matches'][0]['metadata']['description']
        return p
    elif closest_category=="helpline":
        job_result = index_3.query(vector=[input_embedding], top_k=1,include_values=True,
        include_metadata=True)
        p=job_result['matches'][0]['metadata']['description']
        response=text_generate(text,p)
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    elif closest_category=="others":
        return "job somporkito totho ba career somporkito totho jante sahajjo kori ami"
    else:
        return "Nothing"

# Define a Pydantic model for the request body
class MessageRequest(BaseModel):
    message: str

# Define the POST endpoint to process the incoming message
@app.post("/process-message")
async def process_message(request: MessageRequest):
    # Check if the message is "job khujchi"
    if request.message:
        category = classify_text(request.message)
        return {"response": category}

# Optionally, you can also define a root endpoint if needed
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app"}
