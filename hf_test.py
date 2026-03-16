# hf_test.py

import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(
    model="distilbert-base-uncased-finetuned-sst-2-english",
    token=os.getenv("HF_TOKEN"),
)

result = client.text_classification("I love this!")

print(result)