# Usage: source login.devops.sh

PROFILE="management-devops"

aws sso login --profile "$PROFILE"
export AWS_PROFILE=$PROFILE
aws sts get-caller-identity