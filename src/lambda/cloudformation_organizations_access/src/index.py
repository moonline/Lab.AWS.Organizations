import boto3
from crhelper import CfnResource
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from helpers import is_service_enabled


logger = Logger()
cloudformation_client = boto3.client('cloudformation')
cfn_helper = CfnResource(
    json_logging=True,
    log_level='DEBUG',
    boto_level='CRITICAL'
)


@logger.inject_lambda_context()
def handler(event: dict, context: LambdaContext) -> dict:
    '''
    :param event: Cloudformation custom resource event. Example:
        {
            "RequestType": "Create",
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:cloudformation-organizations-access-prod",
            "ServiceTimeout": "30",
            "ResponseURL": "https://cloudformation-custom-resource-response-eucentral1.s3.eu-central-1.amazonaws.com/arn%3Aaws%3Acloudformation%3Aeu-central-1%3A123456789012%3Astack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed%7CEnableCloudformationOrganizationsAccessCustomResource%7Ccf15d843-c0bd-4acf-8fae-39b081702487?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240615T053818Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA...615%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=a314...2194",
            "StackId": "arn:aws:cloudformation:eu-central-1:123456789012:stack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed",
            "RequestId": "uuvvwwxx-5566-yyzz-6677-ffgghhiijjkk",
            "LogicalResourceId": "EnableCloudformationOrganizationsAccessCustomResource",
            "ResourceType": ""AWS::CloudFormation::CustomResource",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:cloudformation-organizations-access-prod",
                "ServiceTimeout": "30"
            }
        }
    :type event: dict
    '''
    return cfn_helper(event, context)


@cfn_helper.create
def create(event, context):
    '''
    Activate trusted access between StackSets and Organizations
    '''
    if not is_service_enabled(cloudformation_client):
        activate_response = cloudformation_client.activate_organizations_access()
        '''
        Example response:
        {
            "ResponseMetadata": {
                "RequestId": "d20b35b2-fc1d-423e-8d12-a569d5f53cd1",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "d20b35b2-fc1d-423e-8d12-a569d5f53cd1",
                    "date": "Mon, 17 Jun 2024 13:45:05 GMT",
                    "content-type": "text/xml",
                    "content-length": "283",
                    "connection": "keep-alive"
                },
                "RetryAttempts": 0
            }
        }
        '''
        logger.info(
            'activate_response',
            extra={'activate_response': activate_response}
        )
    else:
        logger.info(f'trusted access already active')

    return 'cloudformation_organizations_access'


@cfn_helper.update
def update(event, context):
    pass


@cfn_helper.delete
def delete(event, context):
    '''
    Activate trusted access between StackSets and Organizations
    '''

    if is_service_enabled(cloudformation_client):
        deactivate_response = cloudformation_client.deactivate_organizations_access()
        logger.info(
            'deactivate_response',
            extra={'deactivate_response': deactivate_response}
        )
    else:
        logger.info(f'trusted access already inactive')

    return 'cloudformation_organizations_access'
