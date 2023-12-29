import requests
import os
payload = {
    "input_face": "https://storage.googleapis.com/dara-c1b52.appspot.com/daras_ai/media/8c1b1f02-5f66-11ed-a8a9-02420a0000aa/ezgif-5-4ccc215641.gif",
    "input_audio": "https://storage.googleapis.com/dara-c1b52.appspot.com/daras_ai/media/8d3f18d4-5f66-11ed-a8a9-02420a0000aa/al-hitchcock-arpa-Merry_Christmas__Jon%203.wav",
}

response = requests.post(
    "https://api.gooey.ai/v2/Lipsync/",
    headers={
        "Authorization": "Bearer " + os.environ["GOOEY_API_KEY"],
    },
    json=payload,
)
assert response.ok, response.content

result = response.json()
print(response.status_code, result)