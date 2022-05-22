import json
import csv
import boto3
import os
import uuid



def lambda_handler(event, context):
    print('Se han encontrado {} archivo(s) en el bucket nuevo(s)'.format(len(event['Records'])))
    
    print(event)

    # Comenzamos la ejecución del crawler

    response = boto3.client('glue').start_crawler(
        Name= os.environ.get('CRAWLER_NAME')
    )
    print (response)
