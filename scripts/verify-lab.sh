#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

for command_name in aws curl python3; do
  require_command "$command_name"
done
require_region
load_stack_name

STACK_STATUS="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$LAB_STACK" --query 'Stacks[0].StackStatus' --output text)"
[[ "$STACK_STATUS" == "CREATE_COMPLETE" ]] || die "Estado inesperado del stack: $STACK_STATUS"
echo "OK: stack en CREATE_COMPLETE"

ASG_NAME="$(stack_output AutoScalingGroupName)"
TARGET_GROUP_ARN="$(stack_output TargetGroupArn)"
PORTAL_URL="$(stack_output PortalUrl)"

# Las comillas simples protegen los backticks propios de JMESPath.
# shellcheck disable=SC2016
POLICY_COUNT="$(aws autoscaling describe-policies --region "$REGION" --auto-scaling-group-name "$ASG_NAME" --query 'length(ScalingPolicies[?PolicyType==`StepScaling`])' --output text)"
[[ "$POLICY_COUNT" -ge 2 ]] || die "No se encontraron las dos politicas de escalado"
echo "OK: politicas de scale-out y scale-in presentes"

# shellcheck disable=SC2016
HEALTHY_COUNT="$(aws elbv2 describe-target-health --region "$REGION" --target-group-arn "$TARGET_GROUP_ARN" --query 'length(TargetHealthDescriptions[?TargetHealth.State==`healthy`])' --output text)"
[[ "$HEALTHY_COUNT" -ge 1 ]] || die "No hay targets saludables"
echo "OK: $HEALTHY_COUNT target(s) saludable(s)"

RESPONSE="$(curl --fail --silent --show-error --max-time 10 "$PORTAL_URL/")"
python3 -c 'import json,sys; data=json.load(sys.stdin); assert data["service"]=="ucab-enrollment-portal" and data["version"]=="week-1"' <<< "$RESPONSE"
echo "OK: el portal responde con el contrato esperado"

DASHBOARD_NAME="$(stack_output DashboardName)"
aws cloudwatch get-dashboard --region "$REGION" --dashboard-name "$DASHBOARD_NAME" >/dev/null
echo "OK: dashboard de operaciones disponible"

LOG_BUCKET="$(stack_output AccessLogBucketName)"
# shellcheck disable=SC2016
LOGGING_ENABLED="$(aws elbv2 describe-load-balancer-attributes --region "$REGION" --load-balancer-arn "$(stack_output LoadBalancerArn)" --query 'Attributes[?Key==`access_logs.s3.enabled`].Value | [0]' --output text)"
[[ "$LOGGING_ENABLED" == "true" ]] || die "Los logs de acceso del ALB no estan habilitados"
echo "OK: logs de acceso habilitados en $LOG_BUCKET"
echo "VERIFICACION DE SEMANA 1 APROBADA"
