from aws_cdk import (
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_lambda,
    aws_s3 as s3,
    aws_s3_notifications,
    aws_events_targets as targets,

    aws_events as events,
    aws_glue_alpha as glue,
    aws_glue,
    aws_iam as iam,

)
from constructs import Construct

STACK_NAME = 'STARTING-ETL-FROM-FILE'
S3_RAW_PREFIX = ''


PYTHON_BASE_CONFIG = BASE_LAMBDA_CONFIG = dict (
    timeout=Duration.seconds(20),       
    memory_size=128, 
    tracing= aws_lambda.Tracing.ACTIVE,
    runtime = aws_lambda.Runtime.PYTHON_3_8)

class AwsFirstStepsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ================================================================================================================
        # INPUT BUCKET / EVENTO / LAMBDA FUNCTION
        # ================================================================================================================

        #Bucket de carga de archivos

        input_bucket = s3.Bucket(self,"input_files")

        #Function que se gatilla con el nuevo archivo

        new_file_lambda = aws_lambda.Function (
            self,"process_new_file", 
            function_name=f"process_new_file-{STACK_NAME}",
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset("./lambdas/process_new_file/"),
            **PYTHON_BASE_CONFIG,environment={}
        )

        # Evento de notificación 

        new_object = aws_s3_notifications.LambdaDestination(new_file_lambda)

        # Aca le agregamos la notificacion al bucket para que invoque la lambda cuando haya un nuevo objeto

        input_bucket.add_event_notification(s3.EventType.OBJECT_CREATED, new_object)

        # ================================================================================================================
        # GLUE DATABASE / CRAWLER
        # ================================================================================================================

        # Base de datos Glue donde se almacenarán los datos 

        glue_db = glue.Database(self, "demo_etl",database_name="demo_db")

        # Rol de ejecución con los permisos de glue necesarios 

        statement = iam.PolicyStatement( actions=["s3:GetObject","s3:PutObject"],
            resources=[
                "arn:aws:s3:::{}".format(input_bucket.bucket_name),
                "arn:aws:s3:::{}/*".format(input_bucket.bucket_name)])

        # write_to_s3_policy = iam.PolicyDocument(statements=[statement])
        
        glue_role = iam.Role(
                self, 'crawler', role_name = 'CrawlerDemoCDK',
                #inline_policies=[write_to_s3_policy],
                assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
                managed_policies = [ iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSGlueServiceRole')]
            )
        
        glue_role.add_to_policy(statement)

        # Crawler para la ejecución del escaneo y descubrimiento de datos en los archivos
        # Este crawler crea o actualiza las tablas en Catálogo de datos


        glue_crawler = aws_glue.CfnCrawler(
            self, 'glue-crawler', description="Rastreador para nuevos datos raw",
            name=f'raw-crawler-{STACK_NAME}',
            database_name=glue_db.database_name,
            schedule=None,
            role=glue_role.role_arn,
            table_prefix="demoetl_",
            targets={"s3Targets": [{"path": "s3://{}/{}".format(input_bucket.bucket_name, S3_RAW_PREFIX)}]}
        )


        # finalmente le pasamos en la variable de entorno el nombre del crawler

        new_file_lambda.add_environment("CRAWLER_NAME", glue_crawler.name)

        # Necesitamos esto para poder invocar la función

        new_file_lambda.add_to_role_policy(iam.PolicyStatement(actions=["glue:StartCrawler"], resources=["*"]))



        # ================================================================================================================
        # EVENTO PARA FINALIZACION DEL CRAWLER / LAMBDA FUNCTION QUE ACTUALIZA DATASET
        # ================================================================================================================

        # regla de event bridge para capturar la finalización del crawler

        event_rule = events.Rule(self, 'crawler_state_change',description='Detecta cambios del crawler',
            event_pattern=events.EventPattern(
                source=['aws.glue'],
                detail_type=['Glue Crawler State Change'],
                detail={"state": [ "Succeeded","Failed"]})
        )


        # Lambda para ejecutar cuando termine el crawler

        post_crawler_lambda = aws_lambda.Function (
            self,"post_crawler", function_name=f"post_crawler-{STACK_NAME}",
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset("./lambdas/post_crawler/"),
            **PYTHON_BASE_CONFIG,environment={})

        # Asignamos el Target

        event_rule.add_target(targets.LambdaFunction(handler=post_crawler_lambda))





