from typing import Literal
import time

import boto3
from mypy_boto3_organizations.client import OrganizationsClient
from aws_lambda_powertools import Logger


logger = Logger()
organizations_client: OrganizationsClient = boto3.client('organizations')


ENABLE_DISABLE_POLICY_WAIT_ATTEMPTS: int = 10
ENABLE_DISABLE_POLICY_WAIT_DELAY_SECONDS: int = 2
POLICY_TYPE_STATUS_CHANGE_WAIT_DELAY_SECONDS: int = 5


PolicyType = Literal[
    'SERVICE_CONTROL_POLICY',
    'TAG_POLICY',
    'BACKUP_POLICY',
    'AISERVICES_OPT_OUT_POLICY'
]
PolicyTypeStatus = Literal[
    'ENABLED',
    'PENDING_ENABLE',
    'DISABLED',
    'PENDING_DISABLE'
]


class OrganizationService:
    def __init__(self, organizations_client: OrganizationsClient = organizations_client) -> 'OrganizationService':
        self.organizations_client = organizations_client

    @property
    def root(self) -> dict:
        """
        :return: An organization root instance
        :rtype: {
            'Id': 'string',
            'Arn': 'string',
            'Name': 'string',
            'PolicyTypes': [
                {
                    'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                    'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                },
            ]
        }
        """
        list_roots_paginator = organizations_client.get_paginator(
            'list_roots'
        )
        '''
        Response syntax:
        {
            'Roots': [
                {
                    'Id': 'string',
                    'Arn': 'string',
                    'Name': 'string',
                    'PolicyTypes': [
                        {
                            'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                            'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                        },
                    ]
                },
            ],
            'NextToken': 'string'
        }
        '''
        roots = [
            root
            for roots in list_roots_paginator.paginate()
            for root in roots['Roots']
        ]

        # There should only be one organization root
        # See https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html
        if len(roots) == 1:
            return roots[0]
        elif len(roots) > 1:
            logger.warning('Multiple roots found!', extra={'roots': roots})
            return roots[0]
        else:
            raise Exception(
                'No organizations root found! Ensure AWS Organizations is enabled'
            )

    @property
    def organization(self) -> list[dict]:
        '''
        :return: Available policy types
        :rtype: {
            'Id': 'string',
            'Arn': 'string',
            'FeatureSet': 'ALL'|'CONSOLIDATED_BILLING',
            'MasterAccountArn': 'string',
            'MasterAccountId': 'string',
            'MasterAccountEmail': 'string',
            'AvailablePolicyTypes': [
                {
                    'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                    'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                },
            ]
        }
        '''
        describe_organization_response = self.organizations_client.describe_organization()
        '''
        Response syntax:
        {
            'Organization': {
                'Id': 'string',
                ...
                'AvailablePolicyTypes': [
                    {
                        'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                        'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                    },
                ]
            }
        }
        '''
        if not 'Organization' in describe_organization_response:
            raise Exception(
                f'No organization found! Ensure AWS Organizations is enabled'
            )

        return describe_organization_response.get('Organization', {})

    def get_policy_type_status(self, policy_type: PolicyType) -> PolicyTypeStatus:
        # root.PolicyTypes and Organization.AvailablePolicyTypes API responses are not consistent.
        # Use only root.PolicyTypes!
        available_policy_types = self.root.get('PolicyTypes', [])

        status = [
            available_policy_type['Status']
            for available_policy_type in available_policy_types
            if available_policy_type['Type'] == policy_type
        ]
        if len(status) == 0:
            return 'DISABLED'
        elif len(status) > 1:
            raise Exception(
                f'More than one status found for "{policy_type}"! This is an AWS service error and should never happen.'
            )
        else:
            return status[0]

    def is_policy_type_enabled(self, policy_type: PolicyType) -> bool:
        '''
        Waits until policy type is not pending anymore (= not existing, 'ENABLED' or 'DISABLED)
        and returns if it is enabled
        '''
        attempt: int = 1
        while attempt <= ENABLE_DISABLE_POLICY_WAIT_ATTEMPTS:
            status = self.get_policy_type_status(policy_type)
            if status == 'ENABLED':
                return True
            elif status == 'DISABLED':
                return False
            else:
                logger.info(
                    'Policy type pending',
                    extra={
                        'policy_type': policy_type,
                        'status': status
                    }
                )
                attempt = attempt + 1
                time.sleep(ENABLE_DISABLE_POLICY_WAIT_DELAY_SECONDS)

        raise Exception(
            f'Policy type "{policy_type}" still pending! Status: "{status}", Expected: "{expected_status}".'
        )

    def enable_policy_type(self, policy_type: PolicyType):
        if not self.is_policy_type_enabled(policy_type):
            enable_policy_type_response = self.organizations_client.enable_policy_type(
                RootId=self.root['Id'],
                PolicyType=policy_type
            )
            # Policy type changes are not reflected inmediately on the API response.
            # Wait to ensure it is up to date
            time.sleep(POLICY_TYPE_STATUS_CHANGE_WAIT_DELAY_SECONDS)
            """
            Response syntax:
            {
                'Root': {
                    'Id': 'string',
                    'Arn': 'string',
                    'Name': 'string',
                    'PolicyTypes': [
                        {
                            'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                            'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                        },
                    ]
                }
            }
            """
            logger.info(
                'enable_policy_type_response',
                extra={'enable_policy_type_response': enable_policy_type_response}
            )

            if not self.is_policy_type_enabled(policy_type):
                raise Exception(
                    f'Enabling policy type "{policy_type}" failed!'
                )
            logger.info(f'Enabled policy type "{policy_type}".')
        else:
            logger.info(f'Policy type "{policy_type}" already enabled')

    def disable_policy_type(self, policy_type: PolicyType):
        if self.is_policy_type_enabled(policy_type):
            disable_policy_type_response = self.organizations_client.disable_policy_type(
                RootId=self.root['Id'],
                PolicyType=policy_type
            )
            # Policy type changes are not reflected inmediately on the API response.
            # Wait to ensure it is up to date
            time.sleep(POLICY_TYPE_STATUS_CHANGE_WAIT_DELAY_SECONDS)
            """
            Response syntax:
            {
                'Root': {
                    'Id': 'string',
                    'Arn': 'string',
                    'Name': 'string',
                    'PolicyTypes': [
                        {
                            'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                            'Status': 'ENABLED'|'PENDING_ENABLE'|'PENDING_DISABLE'
                        },
                    ]
                }
            }
            """
            logger.info(
                'disable_policy_type_response',
                extra={'disable_policy_type_response': disable_policy_type_response}
            )

            if self.is_policy_type_enabled(policy_type):
                raise Exception(
                    f'Disabling policy type "{policy_type}" failed!'
                )
            logger.info(f'Enabled policy type "{policy_type}".')
        else:
            logger.info(f'Policy type "{policy_type}" already disabled')
