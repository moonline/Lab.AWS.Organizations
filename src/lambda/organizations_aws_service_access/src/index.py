import boto3
from crhelper import CfnResource
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from helpers import is_service_enabled


logger = Logger()
organizations_client = boto3.client('organizations')
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
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-aws-service-access-prod",
            "ServiceTimeout": "30",
            "ResponseURL": "https://cloudformation-custom-resource-response-eucentral1.s3.eu-central-1.amazonaws.com/arn%3Aaws%3Acloudformation%3Aeu-central-1%3A123456789012%3Astack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed%7CEnableCloudTrailOrganizationsAccessCustomResource%7Ccf15d843-c0bd-4acf-8fae-39b081702487?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240615T053818Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA...615%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=a314...2194",
            "StackId": "arn:aws:cloudformation:eu-central-1:123456789012:stack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed",
            "RequestId": "uuvvwwxx-5566-yyzz-6677-ffgghhiijjkk",
            "LogicalResourceId": "EnableCloudTrailOrganizationsAccessCustomResource",
            "ResourceType": "Custom::EnableCloudTrailOrganizationsAccess",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-aws-service-access-prod",
                "service": "cloudtrail.amazonaws.com",
                "ServiceTimeout": "30"
            }
        }
    :type event: dict
    '''
    return cfn_helper(event, context)


@cfn_helper.create
def create(event, context):
    '''
    Enable AWS service access.
    See AWS service principals: https://gist.github.com/shortjared/4c1e3fe52bdfa47522cfe5b41e5d6f22
    '''
    service = event['ResourceProperties']['service']

    if not is_service_enabled(organizations_client, service):
        '''
        Example response:
            {
                "ResponseMetadata": {
                    "RequestId": "e17f83d3-cc95-4e98-9f9b-feefb9ba9690",
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {
                        "x-amzn-requestid": "e17f83d3-cc95-4e98-9f9b-feefb9ba9690",
                        "content-type": "application/x-amz-json-1.1",
                        "content-length": "0",
                        "date": "Mon, 17 Jun 2024 07:56:28 GMT"
                    },
                    "RetryAttempts": 0
                }
            }
        '''
        activate_response = organizations_client.enable_aws_service_access(
            ServicePrincipal=service
        )
        logger.info(
            'activate_response',
            extra={'activate_response': activate_response}
        )
    else:
        logger.info(f'service access for "{service}" already enabled')

    # Items stored in cfn_helper.Data will be saved as outputs in the resource in CloudFormation
    cfn_helper.Data.update({
        'Service': service
    })

    return f'aws_service_access-{service}'


@cfn_helper.update
def update(event, context):
    # TODO Service change not yet implemented

    service = event['ResourceProperties']['service']
    return f'aws_service_access-{service}'


@cfn_helper.delete
def delete(event, context):
    '''
    Disable AWS service access.
    See AWS service principals: https://gist.github.com/shortjared/4c1e3fe52bdfa47522cfe5b41e5d6f22
    '''
    service = event['ResourceProperties']['service']

    if is_service_enabled(organizations_client, service):
        deactivate_response = organizations_client.disable_aws_service_access(
            ServicePrincipal=service
        )
        logger.info(
            'deactivate_response',
            extra={'deactivate_response': deactivate_response}
        )
    else:
        logger.info(f'service access for "{service}" already disabled')

    cfn_helper.Data.update({
        'Service': service
    })

    return f'aws_service_access-{service}'
