#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

require_command aws
require_region
load_stack_name

ASG_NAME="$(stack_output AutoScalingGroupName)"
TARGET_GROUP_ARN="$(stack_output TargetGroupArn)"

echo "Stack: $LAB_STACK"
echo "Auto Scaling Group: $ASG_NAME"
aws autoscaling describe-auto-scaling-groups \
  --region "$REGION" \
  --auto-scaling-group-names "$ASG_NAME" \
  --query 'AutoScalingGroups[0].{Min:MinSize,Desired:DesiredCapacity,Max:MaxSize,Instances:Instances[].{Id:InstanceId,Lifecycle:LifecycleState,Health:HealthStatus}}' \
  --output table

echo "Estado de los targets:"
aws elbv2 describe-target-health \
  --region "$REGION" \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Port:Target.Port,State:TargetHealth.State,Reason:TargetHealth.Reason}' \
  --output table
