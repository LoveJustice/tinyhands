import os
import boto3
import re
import sagemaker

role = sagemaker.get_execution_role()
region = sagemaker.Session().boto_region_name

bucket = sagemaker.Session().default_bucket()
prefix = "sagemaker/DEMO-xgboost-dist-script"

import os
import io
import boto3
import json
import csv

#: Define the endpoint's name.
ENDPOINT_NAME = 'autopilot-experiment-6d00f17b55464fc49c45d74362f284ce'
runtime = boto3.client('runtime.sagemaker')

#: Define a test payload to send to your endpoint.
payload = {
    "data":{
        "features": {
            "values": [45,"blue-collar","married","basic.9y",'unknown',"yes","no","telephone","may","mon",461,1,999,0,"nonexistent",1.1,93.994,-36.4,4.857,5191.0]
        }
    }
}

#: Submit an API request and capture the response object.
response = runtime.invoke_endpoint(
EndpointName=ENDPOINT_NAME,
ContentType='application/json',
Body=json.dumps(payload)
)

#: Print the model endpoint's output.
print(response['Body'].read().decode())