from mypy_boto3_cloudformation.client import CloudFormationClient


def is_service_enabled(cloudformation_client: CloudFormationClient) -> bool:
    organizations_access_response = cloudformation_client.describe_organizations_access()
    return organizations_access_response.get('Status') == 'ENABLED'
