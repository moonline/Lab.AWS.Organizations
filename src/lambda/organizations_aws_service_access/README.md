# AWS Organizations service access custom resource

## Syntax

To declare this entity in your AWS CloudFormation template, use the same syntax as Custom Resources.
See https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html.

### YAML

```yaml
Type: AWS::CloudFormation::CustomResource # or Custom::MyCustomResourceTypeName
Properties:
  ServiceTimeout: String
  ServiceToken: String
  service: String
```


## Properties

For `ServiceTimeout` and `ServiceToken` see AWS documentation: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html#aws-resource-cloudformation-customresource-properties.

### `service`

An AWS service principal. Examples see https://gist.github.com/shortjared/4c1e3fe52bdfa47522cfe5b41e5d6f22.  

*Required*: Yes  

*Type*: String  

*Update requires*: Not supported


## Return values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, `Ref` returns an ID in the format `aws_service_access-SERVICE`. Example: `aws_service_access-cloudtrail.amazonaws.com`.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type.


#### `Service`

The service principal of the enabled service.



## Examples

### Enable trusted access with CloudTrail

#### YAML

```yaml
# Cloudformation template.yml

# ...

Resources:
  EnableCloudTrailOrganizationsAccessCustomResource:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      ServiceToken: !Ref organizationsAwsServiceAccessFunctionArn
      ServiceTimeout: 10
      service: "cloudtrail.amazonaws.com"
```
