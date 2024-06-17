import boto3
from crhelper import CfnResource
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext


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
            "ResourceType": "Custom::EnableCloudformationOrganizationsAccess",
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
    logger.info('Handle create')

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_instances.html
    '''
    TODO
    Example response:
        {
            'Instances': [
                {
                    'CreatedDate': datetime(2015, 1, 1),
                    'IdentityStoreId': 'string',
                    'InstanceArn': 'string',
                    'Name': 'string',
                    'OwnerAccountId': 'string',
                    'Status': 'CREATE_IN_PROGRESS'|'DELETE_IN_PROGRESS'|'ACTIVE'
                },
            ],
            'NextToken': 'string'
        }
    '''
    activate_response = cloudformation_client.activate_organizations_access()
    logger.info('activate_response', extra={
                'activate_response': activate_response})

    # Items stored in cfn_helper.Data will be saved
    # as outputs in your resource in CloudFormation
    cfn_helper.Data.update({
        # ,'.join([instance['InstanceArn'] for instance in list_instances_result['Instances']])
        'instances': 'Bla'
    })
    '''
    Example:
        {
            "Status": "SUCCESS",
            "PhysicalResourceId": "SsoAdminListInstances",
            "StackId": "arn:aws:cloudformation:eu-central-1:123456789012:stack/organization/aabbccdd-1234-aabb-1234-aabbccddeeff",
            "RequestId": "uuvvwwxx-5566-yyzz-6677-ffgghhiijjkk",
            "LogicalResourceId": "SsoInstance",
            "Reason": "",
            "Data": {
                "instances": []
            },
            "NoEcho": false
        }
    '''
    logger.info('Helper data', extra={'helper_data': cfn_helper.Data})

    #return 'SsoAdminListInstances'


@cfn_helper.update
def update(event, context):
    logger.info('Handle update')
    pass


@cfn_helper.delete
def delete(event, context):
    logger.info('Handle delete')

    deactivate_response = cloudformation_client.deactivate_organizations_access()

    logger.info('deactivate_response', extra={
                'deactivate_response': deactivate_response})
