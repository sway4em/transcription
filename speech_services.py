import boto3
import pygame
from io import BytesIO

# Initialize Polly client
polly_client = boto3.client('polly', region_name='us-west-2')

def synthesize_speech(text):
    response = polly_client.synthesize_speech(VoiceId='Joanna',
                                              OutputFormat='mp3',
                                              Text=text)
    return response['AudioStream'].read()

def play_audio(audio_data):
    pygame.mixer.init()
    with BytesIO(audio_data) as audio_stream:
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()
        print("Playing audio response...")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
