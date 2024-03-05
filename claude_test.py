import boto3
import json
from botocore.client import Config
from langchain.llms.bedrock import Bedrock

examples = open("examples.txt", "r")
example_list = examples.readlines()
examples.close()

types = {
    'Rules, Regulations, and Ordinances': {
        'Parking Regulations': ['parking tickets', 'parking zones', 'special parking districts', 'street sweeping schedules'],
        'Property and Street Modifications': ['installing traffic signs', 'painting curbs', 'outdoor dining permits', 'tree removal permits'],
        'Zoning and Building Codes': ['zoning classifications', 'building permits', 'municipal codes'],
        'Environmental and Public Space Usage': ['tree management', 'public space usage for events or dining', 'environmental regulations']
    },
    'Document/Plan Specific': {
        'City Planning and Development': ['general plans', 'area-specific plans', 'housing projects', 'infrastructure projects'],
        'Environmental and Sustainability Plans': ['climate change adaptation', 'carbon neutrality goals', 'forest management', 'water usage plans'],
        'Public Services and Utilities': ['water supply', 'storm preparedness', 'flood management']
    },
    'Project Specific': {
        'Infrastructure and Public Works': ['road diets', 'park renovations', 'construction projects', 'storm damage repairs'],
        'Transportation and Mobility Projects': ['bikeway projects', 'parking structures', 'public transit enhancements'],
        'Community and Recreational Projects': ['trail extensions', 'park improvements', 'recreational facilities updates']
    },
    'Meeting Specific': {
        'City Council and Committees': ['city council meetings', 'planning commission', 'tree committee', 'administrative boards'],
        'Project Reviews and Approvals': ['discussion outcomes', 'votes', 'public opinions on projects'],
        'Policy Debates and Statements': ['debates', 'policy positions of city officials', 'public statements on city matters']
    },
    'Website/Announcement Specific': {
        'Event and Program Announcements': ['city events', 'block parties', 'recreational programs'],
        'Public Notices and Alerts': ['service changes', 'emergency alerts', 'public health notices'],
        'Resource Availability': ['locations and availability of city services or resources like sandbags or community pools']
    },
    'Unclassified': {
        'Downtown Development': ['downtown amenities', 'parking', 'housing costs', 'commercial development'],
        'Living and Housing': ['rent averages', 'parking for residents', 'availability of grocery stores']
    }
}


def query_kendra(client, query, index_id, pagesize=10, doctype=None):
    if not doctype:
        response = client.query(
            QueryText=query,
            IndexId=index_id,
            PageSize=pagesize)
    else:
        response = client.query(
            QueryText=query,
            IndexId=index_id,
            AttributeFilter={
                "EqualsTo": {
                    "Key": "_category",
                    "Value": {
                        "StringValue": doctype
                    }
                }
            })
    results = {}

    for query_result in response["ResultItems"]:
        document_id = query_result["DocumentId"]
        title = query_result.get('DocumentTitle', {}).get('Text', '')
        document_text = query_result.get("DocumentExcerpt", {}).get("Text", "")
        metadata = query_result.get("DocumentAttributes", [])

        results[document_id] = {"text": document_text, "metadata": metadata, "title": title}

    return results

def call_claude_with_prompt(text):
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2"
    )
    kwargs = {
        "modelId": "anthropic.claude-v2:1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps({
            "prompt": f"\n\nHuman:{text} " + "\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": ["\n\nHuman:"],
            "anthropic_version": "bedrock-2023-05-31"
        }).encode('utf-8')
    }
    response = bedrock_runtime.invoke_model_with_response_stream(**kwargs)
    stream = response.get('body')
    response_text = ""
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                response_text += json.loads(chunk.get('bytes')).get('completion')
    return response_text

def retrieve(query, kb_id, number_of_results=5):
    profile_name = "public-records-profile"

    session = boto3.Session(profile_name=profile_name)
    bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
    bedrock_client = session.client('bedrock-runtime')
    bedrock_agent_client = session.client("bedrock-agent-runtime", region_name="us-east-1", config=bedrock_config)
    model_kwargs_claude = {
        "temperature": 0,
        "top_k": 10,
        "max_tokens_to_sample": 3000
    }
    llm = Bedrock(model_id="anthropic.claude-v2",
              model_kwargs=model_kwargs_claude,
              client = bedrock_client,)
    response = bedrock_agent_client.retrieve(
        retrievalQuery={'text': query},
        knowledgeBaseId=kb_id,
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': number_of_results
            }
        }
    )
    return response

def main():
    kb_id = "FJ9JWBIKTQ"
    query = input("Enter your query: ")

    response = retrieve(query, kb_id, 5)  
    retrieval_results = response['retrievalResults']

    contexts = [result['content']['text'] for result in retrieval_results]
    context_str = "\n\n".join(contexts)
    prompt_for_claude = f"Based on the following documents: {context_str}"

    claude_response = call_claude_with_prompt(prompt_for_claude)

    print("Claude's Response:\n", claude_response)

if __name__ == "__main__":
    main()
