import pinecone
import json

pinecone.init(api_key="654cc13e-86dc-48b9-80c1-6359c63a94d4", environment="gcp-starter")

pinecone.create_index("quickstart", dimension=8, metric="euclidean")
pinecone.describe_index("quickstart")
index = pinecone.Index("quickstart")

index.upsert(
  vectors=[
    {"id": "vec1", "values": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]},
    {"id": "vec2", "values": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]},
    {"id": "vec3", "values": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]},
    {"id": "vec4", "values": [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]}
  ],
  namespace="ns1"
)

index.upsert(
  vectors=[
    {"id": "vec5", "values": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]},
    {"id": "vec6", "values": [0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]},
    {"id": "vec7", "values": [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]},
    {"id": "vec8", "values": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]}
  ],
  namespace="ns2"
)
print(index.describe_index_stats())
print(index.query(
  namespace="ns1",
  vector=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
  top_k=3,
  include_values=True
))

print(index.query(
  namespace="ns2",
  vector=[0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
  top_k=3,
  include_values=True
))

pinecone.delete_index("quickstart")
