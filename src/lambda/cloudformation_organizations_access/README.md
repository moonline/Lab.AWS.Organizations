# CloudFormation Organizations access custom resource

Describe existing access:

```shell
aws cloudformation describe-organizations-access
```

## Syntax

To declare this entity in your AWS CloudFormation template, use the same syntax as Custom Resources.
See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html.

### YAML

```yaml
Type: Custom::CloudFormationOrganizationsAccess # or AWS::CloudFormation::CustomResource
Properties:
  ServiceTimeout: String
  ServiceToken: String
```


## Properties

For `ServiceTimeout` and `ServiceToken` see AWS documentation: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html#aws-resource-cloudformation-customresource-properties.


## Return values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, `Ref` returns `cloudformation_organizations_access`.


## Examples

### Enable organizations access

#### YAML

```yaml
# Cloudformation template.yml

# ...

Resources:
  EnableCloudFormationOrganizationsAccess:
    Type: Custom::CloudFormationOrganizationsAccess
    Properties:
      ServiceToken: !Ref cloudformationOrganizationsAccessFunctionArn
      ServiceTimeout: 30
```
