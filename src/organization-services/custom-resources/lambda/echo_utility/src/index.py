from crhelper import CfnResource
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext


logger = Logger()
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
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:echo-utility-prod",
            "ServiceTimeout": "30",
            "ResponseURL": "https://cloudformation-custom-resource-response-eucentral1.s3.eu-central-1.amazonaws.com/arn%3Aaws%3Acloudformation%3Aeu-central-1%3A123456789012%3Astack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed%7CVariables%7Ccf15d843-c0bd-4acf-8fae-39b081702487?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240615T053818Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA...615%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=a314...2194",
            "StackId": "arn:aws:cloudformation:eu-central-1:123456789012:stack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed",
            "RequestId": "uuvvwwxx-5566-yyzz-6677-ffgghhiijjkk",
            "LogicalResourceId": "Variables",
            "ResourceType": "Custom::EchoUtility",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:echo-utility-prod",
                "variable1": "someValueX",
                "anotherVariable": "42"
            }
        }
    :type event: dict
    '''
    return cfn_helper(event, context)


@cfn_helper.create
def create(event, context):
    cfn_helper.Data.update({
        **event['ResourceProperties']
    })


@cfn_helper.update
def update(event, context):
    '''
    :param event: Cloudformation custom resource event. Example:
    {
        "RequestType": "Update",
        ...
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-policy-type-prod",
            "ServiceTimeout": "30",
            "variable1": "anotherValueY",
            "anotherVariable": "43"
        },
        "OldResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-policy-type-prod",
            "ServiceTimeout": "30",
            "variable1": "someValueX",
            "anotherVariable": "42"
        }
    }
    '''
    cfn_helper.Data.update({
        **event['ResourceProperties']
    })


@cfn_helper.delete
def delete(event, context):
    '''
    :param event: Cloudformation custom resource event. Example:
    {
        "RequestType": "Delete",
        ...
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-policy-type-prod",
            "ServiceTimeout": "30",
            "variable1": "anotherValueY",
            "anotherVariable": "43"
        }
    }
    '''
    cfn_helper.Data.update({
        **event['ResourceProperties']
    })
