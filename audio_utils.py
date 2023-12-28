import boto3
import time
from io import BytesIO
from pydub import AudioSegment
import simpleaudio as sa

polly_client = boto3.client('polly', region_name='us-west-2')

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
