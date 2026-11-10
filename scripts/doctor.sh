#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

for command_name in aws python3 base64 gzip curl; do
  require_command "$command_name"
done
require_region

echo "OK: herramientas requeridas disponibles"
aws sts get-caller-identity --region "$REGION" --output json >/dev/null
echo "OK: credenciales AWS activas"
aws cloudformation validate-template \
  --region "$REGION" \
  --template-body "file://$REPO_ROOT/infra/lab-stack.yaml" >/dev/null
echo "OK: plantilla CloudFormation valida para AWS"
python3 -m unittest discover -s "$REPO_ROOT/tests" -p 'test_*.py'
echo "DIAGNOSTICO APROBADO: entorno listo en $REGION"
