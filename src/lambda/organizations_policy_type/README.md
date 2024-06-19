# AWS Organizations - Policy Type Custom Resource Function

List existing policy types:

```shell
aws organizations describe-organization  | jq '.Organization.AvailablePolicyTypes'
```

## Syntax

To declare this entity in your AWS CloudFormation template, use the same syntax as Custom Resources.
See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html.

### YAML

```yaml
Type: Custom::OrganizationsPolicyType # or AWS::CloudFormation::CustomResource
DependsOn: Organization
Properties:
  ServiceTimeout: String
  ServiceToken: String
  policyType: String
```


## Properties

For `ServiceTimeout` and `ServiceToken` see AWS documentation: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html#aws-resource-cloudformation-customresource-properties.

### `policyType`

The AWS Organizations policy type to enable.

*Required*: Yes  

*Type*: String  

*Allowed values*: `SERVICE_CONTROL_POLICY | AISERVICES_OPT_OUT_POLICY | BACKUP_POLICY | TAG_POLICY`  

*Update requires*: Not supported


## Return values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, `Ref` returns an ID in the format `organizations_policy_type-POLICY_TYPE`. Example: `organizations_policy_type-service_control_policy`.


## Examples

### Enable trusted access with CloudTrail

#### YAML

```yaml
# Cloudformation template.yml

# ...

Resources:
  EnableSCPOrganizationsPolicyType:
    Type: Custom::OrganizationsPolicyType
    DependsOn: Organization
    Properties:
      ServiceToken: !Ref organizationsPolicyTypeFunctionArn
      ServiceTimeout: 10
      policyType: SERVICE_CONTROL_POLICY
```
