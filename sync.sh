#!/bin/bash

set -euo pipefail

APP_NAME="lms_custom"

LOCAL_APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TENANT_CONFIG="$LOCAL_APP_DIR/deploy-tenants.conf"

show_usage() {
	echo "Usage: $0 TENANT"
	echo ""
	echo "Tenants:"
	if declare -F available_tenants >/dev/null 2>&1; then
		available_tenants | sed 's/^/  /'
	else
		echo "  mcal"
	fi
}

_require_command() {
	local command_name="$1"
	if ! command -v "$command_name" >/dev/null 2>&1; then
		echo "Required command not found: $command_name" >&2
		exit 1
	fi
}

_require_path() {
	local path_value="$1"
	local label="$2"
	if [ ! -e "$path_value" ]; then
		echo "$label not found: $path_value" >&2
		exit 1
	fi
}

_resolve_identity_path() {
	local identity_file="$1"
	if [[ "$identity_file" = /* ]]; then
		echo "$identity_file"
	else
		echo "$LOCAL_APP_DIR/$identity_file"
	fi
}

if [ ! -f "$TENANT_CONFIG" ]; then
	echo "Tenant config not found: $TENANT_CONFIG" >&2
	exit 1
fi

# shellcheck source=/dev/null
source "$TENANT_CONFIG"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
	show_usage
	exit 0
fi

if [ "$#" -ne 1 ]; then
	echo "Tenant is required." >&2
	show_usage >&2
	exit 1
fi

TENANT="$1"

if ! load_tenant_config "$TENANT"; then
	echo "Unknown or unconfigured tenant: $TENANT" >&2
	show_usage >&2
	exit 1
fi

SERVER="$SERVER_USER@$SERVER_HOST"
REMOTE_DIR="$BENCH_DIR/apps/$APP_NAME"
IDENTITY_PATH="$(_resolve_identity_path "$IDENTITY_FILE")"

echo "Validating local setup..."
_require_command rsync
_require_command ssh
_require_path "$IDENTITY_PATH" "SSH identity file"
_require_path "$LOCAL_APP_DIR" "Local app directory"

echo "Deploying $APP_NAME for tenant=$TENANT site=$SITE server=$SERVER"

echo "Ensuring remote app directory exists..."
ssh -i "$IDENTITY_PATH" "$SERVER" <<EOF
set -euo pipefail

if [ ! -d "$BENCH_DIR" ]; then
	echo "Bench directory not found: $BENCH_DIR" >&2
	exit 1
fi

mkdir -p "$REMOTE_DIR"
EOF

echo "Syncing $APP_NAME to $SERVER:$REMOTE_DIR ..."
rsync -avz --delete \
	--exclude '.git' \
	--exclude '__pycache__' \
	--exclude '*.pyc' \
	--exclude '.DS_Store' \
	-e "ssh -i $IDENTITY_PATH" \
	"$LOCAL_APP_DIR/" "$SERVER:$REMOTE_DIR/"

echo "Running remote deployment steps..."
ssh -i "$IDENTITY_PATH" "$SERVER" <<EOF
set -euo pipefail

if [ ! -d "$BENCH_DIR" ]; then
	echo "Bench directory not found: $BENCH_DIR" >&2
	exit 1
fi

if [ ! -d "$REMOTE_DIR" ]; then
	echo "Remote app directory not found: $REMOTE_DIR" >&2
	exit 1
fi

cd "$BENCH_DIR"
"$BENCH_DIR/env/bin/pip" install -e "apps/$APP_NAME"

if ! bench --site "$SITE" list-apps | awk '{print \$1}' | grep -Fxq "$APP_NAME"; then
	bench --site "$SITE" install-app "$APP_NAME"
fi

bench --site "$SITE" migrate
bench restart
EOF

echo "Deployment completed successfully."
