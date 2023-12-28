import pinecone
import json

embeddings_file_path = './embeddings.json'
with open(embeddings_file_path, 'r') as f:
    embeddings = json.load(f)
pinecone.init(api_key="654cc13e-86dc-48b9-80c1-6359c63a94d4", environment="YOUR_ENVIRONMENT")
pinecone.create_index("quickstart", dimension=512, metric="euclidean")
pinecone.describe_index("sounds")
index = pinecone.Index("sounds")

for file_name, emb_vector in embeddings.items():
    index.upsert(vectors=[{"id": file_name, "values": emb_vector}], namespace="your_namespace")

print(index.describe_index_stats())