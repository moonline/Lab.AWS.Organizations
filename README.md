# Lab.AWS.Organizations

A basic setup of an AWS Organization with AWS SAM



## Architecture

```mermaid
---
title: Organization
---
flowchart TB
    root([AWS Organization Root])
    root --- dev(DevelopmentOU)
    dev --- project1(DevProjectOU)
    project1 --- project1Sandbox[DevProject1Sandbox]

    root --- prod(ProductionOU)
```


## Development

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

For instructions regarding SAM, see https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html.

### SAM build

```sh
cd src
```

```sh
# Build template
sam build
```

### SAM deploy

1. Deploy or organization
    ```sh
    sam deploy --config-env prod --parameter-overrides "organizationEmail=aws@your-domain.tld"
    ```

2. Enable Identity Center in AWS Organizations console https://us-east-1.console.aws.amazon.com/organizations/v2/home/services/AWS%20IAM%20Identity%20Center%20(AWS%20Single%20Sign-On)
3. Enable Identity Center in IAM Identity center console https://eu-central-1.console.aws.amazon.com/singlesignon/home?region=eu-central-1#!/
4. Get identity center instance ARN
    ```sh
    aws sso-admin list-instances --region eu-central-1 | jq '.Instances[0].InstanceArn'
    ```
5. Deploy permission sets, roles, etc (replace the ARN with the output from 4)
    ```sh
    sam deploy --config-env prod --parameter-overrides "organizationEmail=aws@your-domain.tld" "identityCenterInstanceArn=arn:aws:sso:::instance/ssoins-***"
    ```


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
