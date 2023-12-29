import boto3, json, threading

def main():
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2"
    )
    kwargs = {
            "modelId": "anthropic.claude-v2:1",
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps({
                "prompt": "\n\nHuman:What is the capital of Cambodia? " + "\n\nAssistant:",
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": [
                "\n\nHuman:"
                ],
                "anthropic_version": "bedrock-2023-05-31"
            }).encode('utf-8')
            }
    response = bedrock_runtime.invoke_model_with_response_stream(**kwargs)
    stream = response.get('body')
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                response_text = json.loads(chunk.get('bytes')).get('completion')
                print(response_text)                
    print('\n\n')
if __name__ == '__main__':
    main()
# import boto3
# polly_client = boto3.Session(
#                 aws_access_key_id='AKIAWTQ5AADJWKD5FC43',
#     aws_secret_access_key='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',
#     region_name='us-west-2').client('polly')
# response = polly_client.synthesize_speech(VoiceId='Joanna',
#                 OutputFormat='mp3',
#                 Text = 'This is a sample text to be synthesized.',
#                 Engine = 'neural')
# file = open('speech.mp3', 'wb')
# file.write(response['AudioStream'].read())
# file.close()