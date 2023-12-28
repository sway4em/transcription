import requests
import os
API_URL = "https://api-inference.huggingface.co/models/dslim/bert-base-NER"
headers = {"Authorization":f"Bearer {os.environ['HF_KEY']}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "My name is Sarah Jessica Parker but you can call me Jessica",
})

for out in output:
    if out["entity_group"] == "PER":
        print(out["word"])