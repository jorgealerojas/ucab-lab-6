#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_FILE="$REPO_ROOT/.ucab-lab-6-stack"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-2}}"

die() {
  echo "ERROR: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Falta el comando requerido: $1"
}

require_region() {
  [[ "$REGION" == "us-east-2" ]] || die "Use us-east-2; region actual: $REGION"
}

load_stack_name() {
  if [[ -n "${STACK_NAME:-}" ]]; then
    LAB_STACK="$STACK_NAME"
  elif [[ -f "$STATE_FILE" ]]; then
    LAB_STACK="$(tr -d '[:space:]' < "$STATE_FILE")"
  else
    die "No se encontro $STATE_FILE. Ejecute primero ./scripts/deploy-lab.sh."
  fi
  [[ "$LAB_STACK" =~ ^ucab-lab-6-[a-f0-9]{16}$ ]] || die "Nombre de stack no valido: $LAB_STACK"
}

stack_output() {
  local output_key="$1"
  aws cloudformation describe-stacks \
    --region "$REGION" \
    --stack-name "$LAB_STACK" \
    --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue | [0]" \
    --output text
}

