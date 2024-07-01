from typing import Literal

import boto3
from mypy_boto3_organizations.client import OrganizationsClient
from aws_lambda_powertools import Logger


logger = Logger()
organizations_client: OrganizationsClient = boto3.client('organizations')


ENABLE_DISABLE_POLICY_WAIT_ATTEMPTS: int = 10
ENABLE_DISABLE_POLICY_WAIT_DELAY_SECONDS: int = 2
POLICY_TYPE_STATUS_CHANGE_WAIT_DELAY_SECONDS: int = 5


class OrganizationService:
    def __init__(self, organizations_client: OrganizationsClient = organizations_client) -> 'OrganizationService':
        self.organizations_client = organizations_client

    def list_delegated_administrators(self, service_principal: str) -> list[dict]:
        '''
        :return: Available delegated administrators
        :rtype: [
            {
                'Id': 'string',
                'Arn': 'string',
                'Email': 'string',
                'Name': 'string',
                'Status': 'ACTIVE'|'SUSPENDED'|'PENDING_CLOSURE',
                'JoinedMethod': 'INVITED'|'CREATED',
                'JoinedTimestamp': datetime(2015, 1, 1),
                'DelegationEnabledDate': datetime(2015, 1, 1)
            }
        ]
        '''
        list_delegated_administrators_paginator = organizations_client.get_paginator(
            'list_delegated_administrators'
        )

        return [
            delegated_administrator
            for delegated_administrators in list_delegated_administrators_paginator.paginate(
                ServicePrincipal=service_principal
            )
            for delegated_administrator in delegated_administrators['DelegatedAdministrators']
        ]

    def list_delegated_services(self, account_id: str) -> list[dict]:
        '''
        :return: Available delegated services
        :rtype: [
            {
                'ServicePrincipal': 'string',
                'DelegationEnabledDate': datetime(2015, 1, 1)
            }
        ]
        '''
        list_delegated_services_for_account_paginator = organizations_client.get_paginator(
            'list_delegated_services_for_account'
        )

        try:
            return [
                delegated_service
                for delegated_services in list_delegated_services_for_account_paginator.paginate(
                    AccountId=account_id
                )
                for delegated_service in delegated_services.get('DelegatedServices', [])
            ]
        except organizations_client.exceptions.AccountNotRegisteredException:
            return []

    def get_delegated_service(self, account_id: str, service_principal: str) -> dict:
        '''
        :return: Delegated service
        :rtype: {
            'ServicePrincipal': 'string',
            'DelegationEnabledDate': datetime(2015, 1, 1)
        }
        '''
        delegated_services = [
            delegated_service
            for delegated_service in self.list_delegated_services(account_id)
            if delegated_service['ServicePrincipal'] == service_principal
        ]

        if len(delegated_services) >= 1:
            if len(delegated_services) > 1:
                # There should only be one instance of the same delegated service per account
                logger.warning(
                    'Multiple delegated services found!',
                    extra={
                        'account_id': account_id,
                        'service_principal': service_principal
                    }
                )

            return delegated_services[0]
        else:
            return None

    def get_delegated_administrator(self, account_id: str, service_principal: str) -> dict:
        delegated_administrators = [
            delegated_administrator
            for delegated_administrator in self.list_delegated_administrators(service_principal)
            if delegated_administrator['Id'] == account_id
        ]

        if len(delegated_administrators) >= 1:
            if len(delegated_administrators) > 1:
                logger.warning(
                    'Multiple delegated administrators found!',
                    extra={
                        'account_id': account_id,
                        'service_principal': service_principal,
                        'delegated_administrators': delegated_administrators
                    }
                )

            return delegated_administrators[0]
        else:
            return None

    def has_delegated_service(self, account_id: str, service_principal: str) -> bool:
        delegated_service = self.get_delegated_service(
            account_id, service_principal
        )
        return delegated_service is not None

    def register_delegated_administrator(self, account_id: str, service_principal: str):
        if not self.has_delegated_service(account_id, service_principal):
            self.organizations_client.register_delegated_administrator(
                AccountId=account_id,
                ServicePrincipal=service_principal
            )

            if not self.has_delegated_service(account_id, service_principal):
                raise Exception(
                    f'Registering delegated administrator for account "{account_id}" and service "{service_principal}" failed!'
                )
            logger.info(
                'Registered delegated administrator.',
                extra={
                    'account_id': account_id,
                    'service_principal': service_principal
                }
            )
        else:
            logger.info(
                'Delegated administrator already registered.',
                extra={
                    'account_id': account_id,
                    'service_principal': service_principal
                }
            )

        delegated_administrator = self.get_delegated_administrator(
            account_id, service_principal
        )
        logger.info(
            'Delegated administrator',
            extra={'delegated_administrator': delegated_administrator}
        )
        return delegated_administrator

    def deregister_delegated_administrator(self, account_id: str, service_principal: str):
        if self.has_delegated_service(account_id, service_principal):
            self.organizations_client.deregister_delegated_administrator(
                AccountId=account_id,
                ServicePrincipal=service_principal
            )

            if self.has_delegated_service(account_id, service_principal):
                raise Exception(
                    f'Deregistering delegated administrator for account "{account_id}" and service "{service_principal}" failed!'
                )
            logger.info(
                'Deregistered delegated administrator.',
                extra={
                    'account_id': account_id,
                    'service_principal': service_principal
                }
            )
        else:
            logger.info(
                'Delegated administrator already deregistered.',
                extra={
                    'account_id': account_id,
                    'service_principal': service_principal
                }
            )
