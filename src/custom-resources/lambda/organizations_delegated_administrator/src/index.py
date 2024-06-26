from crhelper import CfnResource
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from services.organization_service import OrganizationService


logger = Logger()
cfn_helper = CfnResource(
    json_logging=True,
    log_level='DEBUG',
    boto_level='CRITICAL'
)
organizations_service = OrganizationService()


@logger.inject_lambda_context()
def handler(event: dict, context: LambdaContext) -> dict:
    '''
    :param event: Cloudformation custom resource event. Example:
        {
            "RequestType": "Create",
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-delegated-admin-prod",
            "ServiceTimeout": "30",
            "ResponseURL": "https://cloudformation-custom-resource-response-eucentral1.s3.eu-central-1.amazonaws.com/arn%3Aaws%3Acloudformation%3Aeu-central-1%3A123456789012%3Astack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed%7CIdentityCenterDelegatedAdministrator%7Ccf15d843-c0bd-4acf-8fae-39b081702487?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240615T053818Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA...615%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=a314...2194",
            "StackId": "arn:aws:cloudformation:eu-central-1:123456789012:stack/aabbccdd-1234-aabb-1234-aabbccddeeff/0be779b0-16d1-11ef-a3b1-0634a5b1d8ed",
            "RequestId": "uuvvwwxx-5566-yyzz-6677-ffgghhiijjkk",
            "LogicalResourceId": "IdentityCenterDelegatedAdministrator",
            "ResourceType": "Custom::OrganizationsDelegatedAdministrator",
            "ResourceProperties": {
                "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-delegated-admin-prod",
                "accountId": "112233445566",
                "service": "sso.amazonaws.com"
            }
        }
    :type event: dict
    '''
    return cfn_helper(event, context)


@cfn_helper.create
def create(event, context):
    resource_properties = event['ResourceProperties']
    if not ('accountId' in resource_properties and 'service' in resource_properties):
        raise Exception(
            'Parameter "accountId" or "service" missing! Can not register delegated administrator.'
        )

    account_id = resource_properties['accountId']
    service_principal = resource_properties['service']

    delegated_administrator = organizations_service.register_delegated_administrator(
        account_id, service_principal
    )

    if delegated_administrator:
        cfn_helper.Data.update({
            'Id': delegated_administrator['Id'],
            'Arn': delegated_administrator['Arn']
        })

    return f'delegated_admin-{account_id.lower()}-{service_principal.lower().replace(".","_")}'


@cfn_helper.update
def update(event, context):
    '''
    :param event: Cloudformation custom resource event. Example:
    {
        "RequestType": "Update",
        ...
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-delegated-admin-prod",
            "ServiceTimeout": "30",
            "accountId": "112233445566",
            "service": "sso.amazonaws.com"
        },
        "OldResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-delegated-admin-prod",
            "ServiceTimeout": "30",
            "accountId": "112233445566",
            "service": "cloudtrail.amazonaws.com"
        }
    }
    '''
    old_account_id = event['OldResourceProperties']['accountId']
    old_service_principal = event['OldResourceProperties']['service']

    resource_properties = event['ResourceProperties']
    if not ('accountId' in resource_properties and 'service' in resource_properties):
        raise Exception(
            'Parameter "accountId" or "service" missing! Can not update delegated administrator registration.'
        )

    new_account_id = resource_properties['accountId']
    new_service_principal = resource_properties['service']

    organizations_service.deregister_delegated_administrator(
        old_account_id, old_service_principal
    )
    delegated_administrator = organizations_service.register_delegated_administrator(
        new_account_id, new_service_principal
    )
    if delegated_administrator:
        cfn_helper.Data.update({
            'Id': delegated_administrator['Id'],
            'Arn': delegated_administrator['Arn']
        })

    return f'delegated_admin-{new_account_id.lower()}-{new_service_principal.lower().replace(".","_")}'


@cfn_helper.delete
def delete(event, context):
    '''
    :param event: Cloudformation custom resource event. Example:
    {
        "RequestType": "Delete",
        ...
        "ResourceProperties": {
            "ServiceToken": "arn:aws:lambda:eu-central-1:123456789012:function:organizations-delegated-admin-prod",
            "ServiceTimeout": "30",
            "accountId": "112233445566",
            "service": "sso.amazonaws.com"
        }
    }
    '''
    resource_properties = event['ResourceProperties']
    if 'accountId' in resource_properties and 'service' in resource_properties:
        account_id = resource_properties['accountId']
        service_principal = resource_properties['service']

        organizations_service.deregister_delegated_administrator(
            account_id, service_principal
        )
    else:
        # Do not raise an error to not block CloudFormation resource deletion
        logger.error(
            'Parameter missing. Can not deregister administrator.',
            extra={'resource_properties': resource_properties}
        )
