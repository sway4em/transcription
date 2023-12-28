import asyncio
import boto3
import os
from openai import OpenAI
# This example uses the sounddevice library to get an audio stream from the
# microphone. It's not a dependency of the project but can be installed with
# `pip install sounddevice`.
import sounddevice


from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
client = OpenAI(
    # This is the default and can be omitted
    
    api_key=os.environ["OPENAI_API_KEY"]
)

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""
def get_response(message):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

message = ""

# class MyEventHandler(TranscriptResultStreamHandler):
#     async def handle_transcript_event(self, transcript_event: TranscriptEvent):
#         # This handler can be implemented to handle transcriptions as needed.
#         # Here's an example to get started.
#         results = transcript_event.transcript.results
#         for result in results:
#             for alt in result.alternatives:
#                 print(alt.transcript)
                
class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_transcript = ""
        self.partial_transcript = ""
        self.last_final_time = None
        self.silence_threshold = 3  # seconds

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        now = asyncio.get_event_loop().time()
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                self.partial_transcript = ' '.join([alt.transcript for alt in result.alternatives])
                print("Partial:", self.partial_transcript)
            else:
                self.current_transcript = ' '.join([alt.transcript for alt in result.alternatives])
                print("Final:", self.current_transcript)
                self.last_final_time = now

        if self.last_final_time and (now - self.last_final_time) > self.silence_threshold:
            print("Speech considered complete after silence.")
            response = get_response(self.current_transcript)
            print("Response:", response)
            self.current_transcript = ""
            self.partial_transcript = ""
            self.last_final_time = None

async def mic_stream():
    # This function wraps the raw input stream from the microphone forwarding
    # the blocks to an asyncio.Queue.
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    # Be sure to use the correct parameters for the audio stream that matches
    # the audio formats described for the source language you'll be using:
    # https://docs.aws.amazon.com/transcribe/latest/dg/streaming.html
    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )
    # Initiate the audio stream and asynchronously yield the audio chunks
    # as they become available.
    with stream:
        while True:
            indata, status = await input_queue.get()
            yield indata, status


async def write_chunks(stream):
    # This connects the raw audio chunks generator coming from the microphone
    # and passes them along to the transcription stream.
    async for chunk, status in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()


async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="us-west-2")

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="en-US",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(stream), handler.handle_events())


loop = asyncio.get_event_loop()
# loop.run_until_complete(basic_transcribe())
# loop.close()
if __name__ == "__main__":
    asyncio.run(basic_transcribe())