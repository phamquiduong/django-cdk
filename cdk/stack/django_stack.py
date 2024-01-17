import os
from datetime import datetime

from aws_cdk import (Duration, Stack, aws_apigateway, aws_cloudfront, aws_cloudfront_origins, aws_iam, aws_lambda,
                     aws_s3, aws_s3_deployment)
from constructs import Construct

NOW = datetime.now()


class DjangoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.construct_id = construct_id

        self.__create_static_s3_bucket()
        self.__create_static_cloudfront()
        self.__upload_static_file_to_s3()

        self.__create_docker_lambda_function()
        # self.__add_role_policy_cognito()

        self.__create_api_gateway()

    def __create_docker_lambda_function(self):
        path_to_function_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src",)

        is_arm64 = os.getenv('IS_ARM64', 'true').lower() == 'true'
        architecure_config = {'architecture': aws_lambda.Architecture.ARM_64} if is_arm64 else {}

        self.docker_lambda_function = aws_lambda.DockerImageFunction(
            self,
            id=f"{self.construct_id}-Lambda",
            function_name=f'{self.construct_id}-lambda-{NOW.strftime("%Y-%m-%d")}'.lower(),
            code=aws_lambda.DockerImageCode.from_image_asset(path_to_function_folder),
            timeout=Duration.seconds(30),
            **architecure_config,
            environment={
                'IS_ON_LAMBDA': 'true',
                'STATIC_URL': f'https://{self.cloud_front.distribution_domain_name}/'
            },
        )

    def __add_role_policy_cognito(self):
        self.docker_lambda_function.add_to_role_policy(
            aws_iam.PolicyStatement(
                sid='VisualEditor0',
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "cognito-idp:AdminInitiateAuth",
                    "cognito-idp:GetUser",
                    "cognito-idp:AdminRespondToAuthChallenge"
                ],
                resources=['*']
            )
        )

    def __create_api_gateway(self):
        self.lambda_rest_api = aws_apigateway.LambdaRestApi(
            self,
            id=f'{self.construct_id}-API-Gateway',
            handler=self.docker_lambda_function  # type: ignore
        )

    def __create_static_s3_bucket(self):
        self.bucket = aws_s3.Bucket(
            self,
            id=f"{self.construct_id}-Bucket",
            bucket_name=f'{self.construct_id}-bucket-{NOW.strftime("%Y-%m-%d")}'.lower(),
        )

    def __create_static_cloudfront(self):
        self.cloud_front = aws_cloudfront.Distribution(
            self,
            id=f"{self.construct_id}-CloudFront",
            default_behavior=aws_cloudfront.BehaviorOptions(
                allowed_methods=aws_cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                compress=True,
                origin=aws_cloudfront_origins.S3Origin(self.bucket),
                viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            )
        )

    def __upload_static_file_to_s3(self):
        path_to_static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static",)

        self.s3 = aws_s3_deployment.BucketDeployment(
            self,
            id=f"{self.construct_id}-Deployment",
            sources=[aws_s3_deployment.Source.asset(path_to_static_folder)],
            destination_bucket=self.bucket
        )
