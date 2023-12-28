import asyncio
import boto3
import os
from openai import OpenAI
from io import BytesIO
import requests
import sounddevice
import simpleaudio as sa
from pydub import AudioSegment
import time
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
ENABLE_STREAMING = False
synthesis_time = 0
API_URL = "https://api-inference.huggingface.co/models/dslim/bert-base-NER"
headers = {"Authorization":f"Bearer {os.environ['HF_KEY']}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
client = OpenAI(
    # This is the default and can be omitted
    
    api_key=os.environ["OPENAI_API_KEY"]
)
polly_client = boto3.client('polly', region_name='us-west-2')

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

def synthesize_speech(text, output_format='mp3', voice='Joanna', enable_streaming=False):
    start_time = time.time()  # Start the timer

    polly_client = boto3.client('polly', region_name='us-west-2')

    response = polly_client.synthesize_speech(VoiceId=voice,
                                              OutputFormat=output_format,
                                              Text=text)
    synthesis_time = time.time() - start_time  # Measure the time taken

    if enable_streaming:
        if "AudioStream" in response:
            return response['AudioStream']
        else:
            raise Exception("Could not stream audio from Polly response.")
    else:
        if "AudioStream" in response:
            return response['AudioStream'].read()
        else:
            raise Exception("Could not synthesize audio from Polly response.")

def play_audio(audio_data, enable_streaming=False):
    try:
        if enable_streaming:
            with closing(audio_data) as stream:
                audio_data = stream.read()
        audio_segment = AudioSegment.from_file(BytesIO(audio_data), format='mp3')
    except Exception as e:
        print("Error converting audio data:", e)
        return

    try:
        play_obj = sa.play_buffer(
            audio_segment.raw_data,
            num_channels=audio_segment.channels,
            bytes_per_sample=audio_segment.sample_width,
            sample_rate=audio_segment.frame_rate
        )
        play_obj.wait_done()
    except Exception as e:
        print("Error playing audio:", e)


message = ""
                
class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_transcript = ""
        self.partial_transcript = ""
        self.last_final_time = None
        self.silence_threshold = 3  # seconds
        self.person_name = None  # To store the identified person's name

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

                # Check for a person's name if not already found
                if not self.person_name:
                    self.check_for_name(self.current_transcript)

        if self.last_final_time and (now - self.last_final_time) > self.silence_threshold:
            print("Speech considered complete after silence.")
            response = get_response(self.current_transcript)
            print("Response:", response)
            print("Synthesizing response...")
            audio_data = synthesize_speech(response, enable_streaming=ENABLE_STREAMING)
            print(f"Time taken for synthesis: {synthesis_time:.2f} seconds")
            print("Playing audio response...")
            play_audio(audio_data, enable_streaming=ENABLE_STREAMING)
            self.current_transcript = ""
            self.partial_transcript = ""
            self.last_final_time = None

    def check_for_name(self, text):
        output = query({"inputs": text})
        for out in output:
            if out["entity_group"] == "PER":
                self.person_name = out["word"]
                print(f"The person's name is {self.person_name}")
                break  # Stop after identifying the name

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

if __name__ == "__main__":
    asyncio.run(basic_transcribe())