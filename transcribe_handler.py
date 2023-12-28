import asyncio
from amazon_transcribe.model import TranscriptEvent

class MyEventHandler:
    def __init__(self, response_handler, silence_threshold=3):
        self.current_transcript = ""
        self.partial_transcript = ""
        self.last_final_time = None
        self.silence_threshold = silence_threshold
        self.response_handler = response_handler

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
            await self.response_handler(self.current_transcript)
            self.current_transcript = ""
            self.partial_transcript = ""
            self.last_final_time = None
