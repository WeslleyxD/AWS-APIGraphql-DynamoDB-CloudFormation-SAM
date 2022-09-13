import json
import os
import requests

def lambda_handler(event, context):
    session = requests.Session()

    APPSYNC_API_ENDPOINT_URL = os.environ.get('ApiUrl')
    query = """
    query MyQuery {
        listStudents {
            items {
                Email
                ID
            }
        }
    }
    """
    response = session.request(
        url=APPSYNC_API_ENDPOINT_URL,
        method='POST',
        headers={'x-api-key': os.environ.get('ApiKey')},
        json={'query': query}
    )

    responsegql = response.text

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": responsegql,
            # "location": ip.text.replace("\n", "")
        }),
    }