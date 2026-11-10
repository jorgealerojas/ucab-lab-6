#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

for command_name in aws gzip; do
  require_command "$command_name"
done
require_region
load_stack_name

LOG_BUCKET="$(stack_output AccessLogBucketName)"
LATEST_KEY="$(aws s3api list-objects-v2 \
  --region "$REGION" \
  --bucket "$LOG_BUCKET" \
  --query 'reverse(sort_by(Contents,&LastModified))[0].Key' \
  --output text)"

if [[ -z "$LATEST_KEY" || "$LATEST_KEY" == "None" ]]; then
  die "Aun no hay logs. Genere trafico y espere entre 5 y 10 minutos."
fi

echo "Objeto mas reciente: s3://$LOG_BUCKET/$LATEST_KEY"
aws s3 cp "s3://$LOG_BUCKET/$LATEST_KEY" - --region "$REGION" --only-show-errors | gzip -dc | tail -n 10
