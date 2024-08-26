# Lab.AWS.Organizations

A basic setup of an AWS Organization with AWS SAM.

Key concepts see https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html .


## Custom Resources for Cloudformation

CloudFormation is missing some key resources for managing AWS Organizations.
These are covered by the following custom resources:

* Organizations service access: [organizations_aws_service_access](src/custom-resources/lambda/organizations_aws_service_access/README.md)
* Organizations policy type: [organizations_policy_type](src/custom-resources/lambda/organizations_policy_type/README.md)
* Organizations delegated administrator: [organizations_delegated_administrator](src/custom-resources/lambda/delegated_administrator/README.md)
* CloudFormation StackSets organizations access: [cloudformation_organizations_access](src/custom-resources/lambda/cloudformation_organizations_access/README.md)


## Architecture

```mermaid
---
title: Organization
---
%% Icons see https://fontawesome.com/search?m=free
flowchart TB
    classDef account stroke:#CD2264,fill:white;
    classDef unit stroke:#CD2264,stroke-dasharray: 5 5,fill:white;

    organization["fa:fa-sitemap\nAWS\nOrganization"]
    style organization fill:#CD2264,color:white,stroke:none;

    management["fa:fa-box\nManagement\naccount"]
    management:::account

    organization --- organizationRoot[fa:fa-sitemap\nOrganizations root]
    management --- organizationRoot
        organizationRoot:::unit
        organizationRoot --- managementOU["fa:fa-folder-open\nManagement OU"]
            managementOU:::unit
            managementOU --- security["fa:fa-box\nSecurity\naccount"]
                security:::account
        organizationRoot --- developmentOU["fa:fa-folder-open\nDevelopment OU"]
            developmentOU:::unit
            developmentOU --- project1Dev["fa:fa-box\nProject 1 DEV\naccount"]
                project1Dev:::account
            developmentOU --- project1Test["fa:fa-box\nProject 1 TEST\naccount"]
                project1Test:::account
        organizationRoot --- productionOU["fa:fa-folder-open\nProduction OU"]
            productionOU:::unit
            productionOU --- project1Prod["fa:fa-box\nProject 1 PROD\naccount"]
                project1Prod:::account
```


## Development

```mermaid
---
title: Organization deployment
---
%% Icons see https://fontawesome.com/search?m=free
flowchart TB
    classDef account stroke:#CD2264,fill:white;
    classDef unit stroke:#CD2264,stroke-dasharray: 5 5,fill:white;
    classDef stack stroke:black,fill:white;
    classDef lambda stroke:none,fill:#ED7100,color:white;
    classDef apiGateway stroke:none,fill:#E7157B,color:white;
    classDef dynamoDB stroke:none,fill:#C925D1,color:white;
    classDef cloudwatchLogs stroke:none,fill:#E7157B,color:white;
    classDef component stroke:black,stroke-dasharray: 5 5,fill:none;
    classDef customResource stroke:none,fill:#E7157B,color:white;
    classDef policies stroke:#DD344C,stroke-width:3px,fill:white;

    subgraph organizationStack ["fa:fa-layer-group Organization Stack"]
        direction LR

        organization["fa:fa-sitemap\nAWS\nOrganization"]
            style organization fill:#CD2264,color:white,stroke:none;
            organization --- organizationalUnits["fa:fa-folder-open\nOrganizational\nunits"]
                organizationalUnits:::unit
                organizationalUnits --- accounts["fa:fa-box\nAccounts"]
                    accounts:::account
    end
        organizationStack:::stack

    organizationStack --> enableIdentityCenter{{"fa:fa-hands\nEnable Identity Center\nmanually in AWS\nConsole"}}
        style enableIdentityCenter fill:tomato,stroke:none,color:white;

    organizationServicesStack["fa:fa-layer-group Organization Services Stack"]
        organizationServicesStack:::stack

    enableIdentityCenter --> organizationServicesStack

    subgraph customResourcesStack ["fa:fa-layer-group Custom Resources Stack"]
        direction TB
        customResources[fa:fa-cubes\nCustom resources]
            customResources:::customResource

            customResources -..- organizationsServiceAccess[λ\nOrganizations\nservice\naccess\nfunction]
                organizationsServiceAccess:::lambda

            customResources -.- organizationsPolicyType[λ\nOrganizations\npolicy\ntype\nfunction]
                organizationsPolicyType:::lambda

            customResources -.- organizationsDelegatedAdministrator[λ\nOrganizations\ndelegated\nadministrator\nfunction]
                organizationsDelegatedAdministrator:::lambda

            customResources -..- cloudFormationOrganizationAccess[λ\nCloudformation\norganization\naccess\nfunction]
                cloudFormationOrganizationAccess:::lambda
    end
        customResourcesStack:::stack
        organizationServicesStack --- customResourcesStack

    subgraph serviceControlPoliciesStack ["fa:fa-layer-group SCP Stack"]
        direction TB
        enableSCPs["fa:fa-cube\nEnable Service\nControl Policies"]
            enableSCPs:::customResource

            enableSCPs --> scps(fa:fa-list-check\nService Control\nPolicies)
                scps:::policies
    end
        serviceControlPoliciesStack:::stack
        organizationServicesStack --- serviceControlPoliciesStack

    subgraph loggingStack ["fa:fa-layer-group Logging Stack"]
        direction TB
        enableCloudTrail["fa:fa-cube\nEnable CloudTrail\norganizations access"]
            enableCloudTrail --> cloudTrailBucket[fa:fa-bucket fa:fa-certificate\nCloudTrail logs\nbucket & policy]
                enableCloudTrail:::customResource
                style cloudTrailBucket stroke:none,fill:#7AA116,color:white;

                cloudTrailBucket --> cloudTrail[fa:fa-table-list\nCloudTrail trail]
                    style cloudTrail stroke:none,fill:#E7157B,color:white;
    end
        loggingStack:::stack
        organizationServicesStack --- loggingStack

    subgraph identityStack ["fa:fa-layer-group Identity Stack"]
        direction TB
        is((•))
        style is stroke:none,fill:none;

        is --- enableSSO["fa:fa-cube\nEnable SSO\norganizations access"]
            enableSSO:::customResource

        is --- registerDelegatedAdmin["fa:fa-cube\nRegister delegated\nadministrator for\nIdentity Center"]
            registerDelegatedAdmin:::customResource

            enableSSO --> enableCloudformation["fa:fa-cube\nEnable Cloudformation\nStackSets organization\naccess"]
                enableCloudformation:::customResource

                enableCloudformation --> managementPolicies(fa:fa-list-check\nManagement account\npolicies)
                    managementPolicies:::policies
                    managementPolicies --> managedPolicies[[fa:fa-certificate\nManaged policies Stackset]]
                        managedPolicies:::stack
                        managedPolicies --> permissionSets(fa:fa-shield-halved\nPermissionSets)
                            permissionSets:::policies
                            permissionSets --> groups[fa:fa-user-group\nGroups]
                                style groups stroke:none,fill:#DD344C,color:white;
    end
        identityStack:::stack
        organizationServicesStack --- identityStack
```


### Dependencies

1. Install latest AWS CLI https://docs.aws.amazon.com/cli/latest/userguide/getting-started-version.html
2. Install AWS SAM CLI https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Install Python 3.9
3. Install jq


### Recommended Visual Studio Code plugins

* https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml
* https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml
* https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one



## Deployment

### A - Deployment role deployment

* By AWS Console:
    1. Login to the AWS Console and open [CloudFormation](https://eu-central-1.console.aws.amazon.com/cloudformation/)
    2. Deploy manually the stack from template `deployment-roles.yml`:
       * Stack Name: `deployment-roles`
       * Capabilities: `CAPABILITY_IAM`
    3. Extract the role ARNs from the outputs
* By AWS CloudShell:
    1. Login to the AWS Console and open [CloudShell](https://eu-central-1.console.aws.amazon.com/cloudshell/)
    2. Upload the file `deployment-roles.yml`
    3. Deploy the stack:

        ```bash
        aws cloudformation deploy \
            --stack-name deployment-roles \
            --template-file deployment-roles.yml \
            --parameter-overrides environment=prod \
            --capabilities CAPABILITY_IAM
        ```

    4. Extract the role ARNs from the outputs:

        ```bash
        aws cloudformation describe-stacks --stack-name deployment-roles | jq -r '.Stacks[].Outputs'
        ```


### B - Organization deployment (`/organization`)

To allow the import of an existing organization, plain CloudFormation is required, because SAM does not support resource import.

1. Validate template file

    ```bash
    cd organization
    aws cloudformation validate-template --template-body file://
organization.yml
    ```

2. Copy `parameters.tmpl.json` to create a parameters file for the corresponding environment, e.g. `parameters.prod.json`. Update the parameters.
3. Deploy the stack, using the deployment role deployed before (adjust the environment):
   * To deploy a new stack or update an existing one:

        ```bash
        aws cloudformation deploy \
            --stack-name organization \
            --role-arn "arn:aws:iam::123456789000:role/deployment/deployment-roles-OrganizationDeploymentRole-abcdefghijkl" \
            --template-file "organization.yml" \
            --parameter-overrides "file://parameters.prod.json"
        ```

   * If there are existing resources:
        Copy and adjust `resources-to-import.tmpl.json`.

        ```bash
        aws cloudformation create-change-set \
            --stack-name organization \
            --role-arn "arn:aws:iam::123456789000:role/deployment/deployment-roles-OrganizationDeploymentRole-abcdefghijkl" \
            --change-set-type IMPORT \
            --change-set-name import-org \
            --template-body "file://organization.yml" \
            --parameters "$(jq -c . parameters.prod.json)" \
            --resources-to-import "file://resources-to-import.prod.json"
        ```

        ```bash
        aws cloudformation describe-change-set \
            --change-set-name import-org \
            --stack-name organization
        ```

        ```bash
        aws cloudformation execute-change-set \
            --change-set-name import-org \
            --stack-name organization
        ```


## C - Organization services deployment `/organization-services`

For instructions regarding SAM, see https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html.

### SAM build

```sh
cd src/organization-services
```

```sh
# Build template
sam build
```

### SAM deploy

1. Enable Identity Center in IAM Identity center console https://eu-central-1.console.aws.amazon.com/singlesignon/home?region=eu-central-1#!/

    **26/06/24**: AWS support confirmed that there is no support to enable IAM Identity Center programatically:

    > Unfortunately, I sincerely regret to convey that enabling AWS IAM Identity Center via API/CLI/boto3 calls is currently not supported. At the moment, there is no alternative method to enable IAM Identity Center other than via the AWS management console. 

3. Get identity center instance ARN
    ```sh
    aws sso-admin list-instances --region eu-central-1 | jq '.Instances[0]'
    ```
4. Enable `IAM user and role access to Billing information` (login with root user):
    * https://us-east-1.console.aws.amazon.com/billing/home#/account
5. Deploy permission sets, roles, etc (replace the ARN with the output from 4)
    ```sh
    sam deploy --config-env prod \
        --role-arn "arn:aws:iam::123456789000:role/deployment/deployment-roles-OrganizationServicesDeploymentRole-abcdefghijkl" \ --parameter-overrides \
        "organizationEmail=aws@your-domain.tld" \
        "identityCenterInstanceArn=arn:aws:sso:::instance/ssoins-***"
    ```

    Alternatively a `samparameters.json` file can be created (see template `samparameters.tmpl.json`)
    and the parameters can be injected when deploying (Change `.prod` to corresponding environment):
    ```sh
    sam deploy --config-env prod \
        --role-arn "arn:aws:iam::123456789000:role/deployment/deployment-roles-OrganizationServicesDeploymentRole-abcdefghijkl" \
        --parameter-overrides \
        $(cat samparameters.json | jq -r '.prod | to_entries | map([.key, .value]|join("=")) | join(" ")')
    ```

6. Create users and assign them to accounts and permission sets https://eu-central-1.console.aws.amazon.com/singlesignon/home?region=eu-central-1#!/instances/


### Get outputs

```sh
# Stack outputs
sam list stack-outputs --stack-name organization
```

### Cleanup

```sh
# Delete stack
sam delete --config-env prod
# or
aws cloudformation delete-stack --stack-name organization

# Cleanup the ORG
aws organizations delete-organization

# To remove all SAM resources completely, the SAM bucket needs to be emptied and the stack aws-sam-cli-managed-default needs to be deleted
# see https://towardsthecloud.com/aws-cli-empty-s3-bucket
sam_bucket=$(aws cloudformation describe-stack-resource --stack-name aws-sam-cli-managed-default --logical-resource-id SamCliSourceBucket | jq -r '.StackResourceDetail.PhysicalResourceId')
aws s3 rm "s3://$sam_bucket" --recursive
aws s3api delete-objects \
    --bucket "$sam_bucket" \
    --delete "$(aws s3api list-object-versions \
        --bucket $sam_bucket | \
        jq '{Objects: [.Versions[] | {Key:.Key, VersionId : .VersionId}], Quiet: false}' \
    )"
aws s3api delete-objects \
    --bucket "$sam_bucket" \
    --delete "$(aws s3api list-object-versions \
        --bucket $sam_bucket | \
        jq '{Objects: [.DeleteMarkers[] | {Key:.Key, VersionId : .VersionId}], Quiet: false}' \
    )"
aws cloudformation delete-stack --stack-name aws-sam-cli-managed-default
```


## Administration

### Switch role to access `OrganizationAccountAccess` of a member account

Use a user with Administrator permissions or an IAM user participating in the IAM group `ManagementAdministrator` to get the permissions to switch role.

See https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_access.html#orgs_manage_accounts_access-cross-account-role