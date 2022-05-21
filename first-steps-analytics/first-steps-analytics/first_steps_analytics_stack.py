from aws_cdk import (
    # Duration,
    Stack,
    core,
    aws_s3 as s3,
    aws_s3_notifications,
    aws_lambda,
    # aws_sqs as sqs,
)
from constructs import Construct

class FirstStepsAbalyticsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REGION_NAME = 'us-east-1'

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++Creamos el data bucket +++++++++++++++++++++++++++++++
        #+++++++El cual será el encargado de recibir los archivos.+++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        bucket1 = s3.Bucket(self,"input-bucket" ,  versioned=False, removal_policy=core.RemovalPolicy.DESTROY)


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++ Creamos la lambda que lee el bucket ++++++++++++++++++++++++
        #Esta se gatillara al entrar un nuevo archivo al bucket input-bucket.+++
        #+++ y activa el Crawler para que actualice el catalogo de glue ++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_read_bucket_trigger_crawler= aws_lambda.Function(self, "lambda_read_bucket_trigger_crawler",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = core.Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda que lee bucket y activa crawler",
                                    code = aws_lambda.Code.asset("./lambda_read_bucket_trigger_crawler"),
                                    environment = {
                                        'ENV_REGION_NAME': REGION_NAME}
                                    )

        #Permiso para leer en S3 y se agrega el evento que la activara 
        bucket1.grant_read(lambda_read_bucket_trigger_crawler) 
        notification = aws_s3_notifications.LambdaDestination(lambda_read_bucket_trigger_crawler)
        bucket1.add_event_notification(s3.EventType.OBJECT_CREATED, notification) 

