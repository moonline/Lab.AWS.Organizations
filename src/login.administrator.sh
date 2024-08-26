# Usage: login.administrator.sh

PROFILE="management-administrator"

aws sso login --profile "$PROFILE"
export AWS_PROFILE=$PROFILE
aws sts get-caller-identity