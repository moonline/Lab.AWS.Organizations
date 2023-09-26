# Lab.AWS.Organizations

A basic setup of an AWS Organization with AWS SAM


## Requirements

1. Install latest AWS CLI https://docs.aws.amazon.com/cli/latest/userguide/getting-started-version.html
2. Install AWS SAM CLI https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
3. Install jq


### Recommended Visual Studio Code plugins

* https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml
* https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml
* https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one



## Deployment

For instructions regarding SAM, see https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html.

```sh
cd src
```

```sh
# Build & deploy
sam deploy --config-env prod
```


```sh
# Stack outputs
sam list stack-outputs --stack-name organization
```


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
