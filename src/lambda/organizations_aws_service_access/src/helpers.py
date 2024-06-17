from mypy_boto3_organizations.client import OrganizationsClient


def list_enabled_service_access(organizations_client: OrganizationsClient) -> list[str]:
    list_service_access_paginator = organizations_client.get_paginator(
        'list_aws_service_access_for_organization'
    )
    return [
        service['ServicePrincipal']
        for page in list_service_access_paginator.paginate()
        for service in page['EnabledServicePrincipals']
    ]


def is_service_enabled(organizations_client: OrganizationsClient, service_principal: str) -> bool:
    enabled_services = list_enabled_service_access(organizations_client)
    return service_principal in enabled_services
