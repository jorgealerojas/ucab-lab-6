#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

require_command aws
require_region
load_stack_name

LOG_BUCKET="$(stack_output AccessLogBucketName)"
echo "Stack seleccionado para limpieza: $LAB_STACK"
echo "Vaciando exclusivamente su bucket de logs: $LOG_BUCKET"
aws s3 rm "s3://$LOG_BUCKET" --recursive --region "$REGION" --only-show-errors

echo "Solicitando la eliminacion del stack..."
aws cloudformation delete-stack \
  --region "$REGION" \
  --stack-name "$LAB_STACK"

echo "Esperando la confirmacion de CloudFormation..."
delete_retries=0
deleted=false
for _ in {1..90}; do
  if ! stack_status="$(aws cloudformation describe-stacks \
    --region "$REGION" \
    --stack-name "$LAB_STACK" \
    --query 'Stacks[0].StackStatus' \
    --output text 2>/dev/null)"; then
    deleted=true
    break
  fi

  if [[ "$stack_status" == "DELETE_FAILED" ]]; then
    ((delete_retries += 1))
    [[ "$delete_retries" -le 3 ]] || die "El stack continua en DELETE_FAILED despues de tres reintentos"
    echo "CloudFormation recibio un log tardio; vaciando nuevamente el mismo bucket..."
    aws s3 rm "s3://$LOG_BUCKET" --recursive --region "$REGION" --only-show-errors
    aws cloudformation delete-stack --region "$REGION" --stack-name "$LAB_STACK"
  elif [[ "$stack_status" != "DELETE_IN_PROGRESS" ]]; then
    die "Estado inesperado durante la limpieza: $stack_status"
  fi
  sleep 5
done

[[ "$deleted" == "true" ]] || die "La limpieza excedio el tiempo de espera"

rm -f "$STATE_FILE"
echo "LIMPIEZA COMPLETA: $LAB_STACK ya no existe"
