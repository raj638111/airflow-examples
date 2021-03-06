
from airflow.providers.pagerduty.hooks.pagerduty import PagerdutyHook
import boto3
import base64
from botocore.exceptions import ClientError
from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from pprint import pprint
from airflow.operators.python import PythonOperator

def get_secret():
    secret_name = "pagerduty/raj"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        #print(get_secret_value_response)
        #print(type(get_secret_value_response))
        #for pair in get_secret_value_response.items():
        #    print(pair)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            #print(eval(secret))
            #print(secret)
            # Convert string representation of dictionary into actual dictionary
            return eval(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret

    # Your code goes here.


def test():
    # secret = get_secret()
    # token = secret['token']
    # routing_key = secret['routing_key']
    # print(type(secret))
    # print(token)
    # print(routing_key)
    hook = PagerdutyHook(token = '')
    response = hook.create_event(summary="some summary",
                                 severity="info",
                                 source="somesource",
                                 routing_key=routing_key,
                                 action="trigger")
    print(response)

test()

# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'start_date': days_ago(2),
#     'email': ['airflow@example.com'],
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 0,
#     'retry_delay': timedelta(minutes=5),
# }
#
# with DAG(
#     'tutorial',
#     default_args=default_args,
#     description='A simple tutorial DAG') as dag:
#
#     def print_context(ds, **kwargs):
#         """Print the Airflow context and ds variable from the context."""
#         pprint(kwargs)
#         print(ds)
#         return 'Whatever you return gets printed in the logs'
#
#     PythonOperator(
#         task_id='print_the_context',
#         python_callable=print_context,
#     )

    # PythonOperator(
    #     task_id='print_the_context',
    #     python_callable=test,
    # )



