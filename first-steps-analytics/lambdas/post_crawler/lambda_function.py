import json
import csv
import boto3
import os
import uuid



def lambda_handler(event, context):
   
    print(event)

    # Cosas para hacer después del crawler
