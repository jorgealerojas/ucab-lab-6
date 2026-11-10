#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./scripts/common.sh
source "$SCRIPT_DIR/common.sh"

require_command aws
require_region
load_stack_name
stack_output PortalUrl
