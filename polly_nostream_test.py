import boto3
import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO
import time

with open('tts_sample_text.txt', 'r') as f:
    sampletext = f.read()

def synthesize_speech(text, output_format='mp3', voice='Joanna'):
    # Initialize the Polly client
    polly_client = boto3.client('polly')

    # Request speech synthesis
    response = polly_client.synthesize_speech(VoiceId=voice,
                                              OutputFormat=output_format,
                                              Text=text,
                                              TextType='text')

    # Return the audio data from the response
    if "AudioStream" in response:
        return response['AudioStream'].read()
    else:
        raise Exception("Could not synthesize audio from Polly response.")

def play_audio(audio_data):
    # Convert audio data to pydub AudioSegment
    try:
        audio_segment = AudioSegment.from_file(BytesIO(audio_data), format='mp3')
    except Exception as e:
        print("Error converting audio data:", e)
        return

    # Play audio using simpleaudio
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

if __name__ == "__main__":
    text_to_speak = sampletext
    try:
        start_time = time.time()  # Start the timer
        audio_data = synthesize_speech(text_to_speak)
        print(f"Time taken for synthesis: {time.time() - start_time:.2f} seconds")

        play_audio(audio_data)
    except Exception as e:
        print("An error occurred:", e)
