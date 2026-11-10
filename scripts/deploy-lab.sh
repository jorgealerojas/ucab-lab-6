#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

require_command aws
require_command python3
require_command base64
require_command gzip
require_region
[[ ! -f "$STATE_FILE" ]] || die "Ya existe un laboratorio registrado en $STATE_FILE"

aws sts get-caller-identity --region "$REGION" >/dev/null
RANDOM_SUFFIX="$(python3 -c 'import secrets; print(secrets.token_hex(8))')"
STACK_NAME="ucab-lab-6-$RANDOM_SUFFIX"
APP_CODE_ARCHIVE_BASE64="$(gzip -c "$REPO_ROOT/app/server.py" | base64 -w 0)"

echo "Identificador generado: $STACK_NAME"
echo "Solicitando la creacion atomica del stack..."
if ! aws cloudformation create-stack \
  --region "$REGION" \
  --stack-name "$STACK_NAME" \
  --template-body "file://$REPO_ROOT/infra/lab-stack.yaml" \
  --parameters "ParameterKey=AppCodeArchiveBase64,ParameterValue=$APP_CODE_ARCHIVE_BASE64" \
  --tags Key=Course,Value=INFO-02028 Key=Lab,Value=unit-6-week-1 \
  --query StackId \
  --output text; then
  die "AWS rechazo la creacion. No se actualizo ningun stack existente."
fi

printf '%s\n' "$STACK_NAME" > "$STATE_FILE"
echo "Creacion aceptada. CloudFormation suele tardar entre 4 y 8 minutos."
if ! aws cloudformation wait stack-create-complete \
  --region "$REGION" \
  --stack-name "$STACK_NAME"; then
  echo "ERROR: CloudFormation no completo el despliegue." >&2
  echo "Revise los eventos del stack $STACK_NAME antes de ejecutar la limpieza." >&2
  exit 1
fi

LAB_STACK="$STACK_NAME"
PORTAL_URL="$(stack_output PortalUrl)"
echo "LABORATORIO LISTO: $STACK_NAME"
echo "Portal: $PORTAL_URL"
echo "Siguiente paso: ./scripts/status.sh"
