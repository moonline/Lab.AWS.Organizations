# AWS Organizations - Delegated Administrator Custom Resource Function

List existing policy types:

```shell
aws organizations list-delegated-administrators | jq '.DelegatedAdministrators'
aws organizations list-delegated-services-for-account --account-id <ACCOUNT_ID> | jq '.DelegatedServices'
```

## Syntax

To declare this entity in your AWS CloudFormation template, use the same syntax as Custom Resources.
See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html.

### YAML

```yaml
Type: Custom::OrganizationsDelegatedAdministrator # or AWS::CloudFormation::CustomResource
DependsOn: Organization
Properties:
  ServiceTimeout: String
  ServiceToken: String
  accountId: String
  service: String
```


## Properties

For `ServiceTimeout` and `ServiceToken` see AWS documentation: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html#aws-resource-cloudformation-customresource-properties.


### `accountId`

The unique identifier (ID) of the AWS Account the delegated administrator will be registered for.

*Required*: Yes  

*Type*: String  

*Update requires*: Resource replacement


### `service`

An AWS service principal. Examples see https://gist.github.com/shortjared/4c1e3fe52bdfa47522cfe5b41e5d6f22.  

*Required*: Yes  

*Type*: String  

*Update requires*: Resource replacement


## Return values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, `Ref` returns an ID in the format `delegated_admin-ACCOUNT_ID-SERVICE`. Example: `delegated_admin-112233445566-sso.amazonaws.com`.


### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type.


#### `Id`

Returns the unique identifier (ID) of the account. For example: `123456789012`.

#### `Arn`

Returns the Amazon Resource Name (ARN) of the account. For example: `arn:aws:organizations::111111111111:account/o-exampleorgid/555555555555`.


## Examples

### Delegated Administrator for IAM Identity Center

#### YAML

```yaml
# Cloudformation template.yml

# ...

Resources:
  IdentityCenterDelegatedAdministrator:
    Type: Custom::OrganizationsDelegatedAdministrator
    DependsOn: Organization
    Properties:
      ServiceToken: !Ref organizationsDelegatedAdministratorFunctionArn
      ServiceTimeout: 10
      accountId: 112233445566
      service: sso.amazonaws.com
```
