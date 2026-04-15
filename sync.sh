#!/bin/bash

SERVER="frappe@mcalfrappe.coreaxissolutions.in"
IDENTITY_FILE="personal"
REMOTE_DIR="/home/frappe/frappe-bench/apps/exam"

echo "Starting sync to $SERVER..."

rsync -avz \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  -e "ssh -i $IDENTITY_FILE" \
  ./ $SERVER:$REMOTE_DIR/

echo "Sync completed! Running bench migrate..."

ssh -i $IDENTITY_FILE $SERVER "
cd /home/frappe/frappe-bench
./env/bin/pip install -e apps/exam || true
bench --site mcalfrappe.coreaxissolutions.in migrate
bench restart
"

echo "Deployment successful!"
