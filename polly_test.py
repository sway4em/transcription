import boto3
from io import BytesIO
import pygame

def synthesize_speech(text, output_format='mp3', voice='Joanna'):
    # Initialize the Polly client
    polly_client = boto3.client('polly')

    # Request speech synthesis
    response = polly_client.synthesize_speech(VoiceId=voice,
                                              OutputFormat=output_format,
                                              Text=text)

    # Access the audio stream from the response
    if "AudioStream" in response:
        return response['AudioStream'].read()
    else:
        raise Exception("Could not stream audio from Polly response.")



def play_audio(audio_data):
    # Initialize pygame mixer
    pygame.mixer.init()

    # Create a BytesIO object from the audio data
    audio_stream = BytesIO(audio_data)

    # Load the audio stream
    pygame.mixer.music.load(audio_stream)

    # Play the audio
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == "__main__":
    text_to_speak = "Hello, this is a test of Amazon Polly."
    try:
        audio_data = synthesize_speech(text_to_speak)
        play_audio(audio_data)
    except Exception as e:
        print("An error occurred:", e)

