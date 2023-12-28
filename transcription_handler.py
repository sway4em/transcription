import asyncio
from audio_utils import synthesize_speech, play_audio
from chat_service import get_response
from ner_service import query
from amazon_transcribe.model import TranscriptEvent
from amazon_transcribe.handlers import TranscriptResultStreamHandler
ENABLE_STREAMING = False
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
            # print(f"Time taken for synthesis: {synthesis_time:.2f} seconds")
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
