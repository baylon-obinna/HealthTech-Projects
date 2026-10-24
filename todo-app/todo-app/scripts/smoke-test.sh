#!/usr/bin/env bash
# Calls the todo API the way a client would: list, create, read, update, delete.
# Exits non-zero if any call returns an unexpected HTTP status.

set -euo pipefail
trap 'echo "❌ Script stopped unexpectedly at line $LINENO (is the app running?)"' ERR

BASE_URL=${BASE_URL:-http://localhost:8080}
API_PATH=${API_PATH:-/api/todos}
CREATE_JSON=${CREATE_JSON:-'{"title":"ci smoke test","completed":false}'}
UPDATE_JSON=${UPDATE_JSON:-'{"title":"ci smoke test (updated)","completed":true}'}
ID_FIELD=${ID_FIELD:-id}

FAILED=0
STATUS=""
BODY=""

# request METHOD URL [JSON_BODY]  ->  sets STATUS and BODY
request() {
  local method=$1 url=$2 data=${3:-} out
  if [ -n "$data" ]; then
    out=$(curl -s --max-time 15 -w $'\n%{http_code}' -X "$method" \
      -H 'Content-Type: application/json' -d "$data" "$url")
  else
    out=$(curl -s --max-time 15 -w $'\n%{http_code}' -X "$method" "$url")
  fi
  STATUS=${out##*$'\n'}
  BODY=${out%$'\n'*}
}

# expect "what we did" "allowed statuses, e.g. 200|201"
expect() {
  if [[ "$STATUS" =~ ^($2)$ ]]; then
    echo "PASS  $1 (HTTP $STATUS)"
  else
    echo "FAIL  $1 (HTTP $STATUS, expected $2)"
    echo "      response: ${BODY:0:300}"
    FAILED=1
  fi
}

echo "Testing $BASE_URL$API_PATH"
echo

request GET "$BASE_URL$API_PATH"
expect "List todos" "200"

request POST "$BASE_URL$API_PATH" "$CREATE_JSON"
expect "Create a todo" "200|201"

ID=$(echo "$BODY" | jq -r ".$ID_FIELD // empty" 2>/dev/null || true)
if [ -z "$ID" ]; then
  echo "FAIL  Could not read '$ID_FIELD' from the create response, so the remaining calls are skipped"
  echo "      response: ${BODY:0:300}"
  exit 1
fi
echo "      created id: $ID"

request GET "$BASE_URL$API_PATH/$ID"
expect "Read the todo back" "200"

request PUT "$BASE_URL$API_PATH/$ID" "$UPDATE_JSON"
expect "Update the todo" "200|204"

request DELETE "$BASE_URL$API_PATH/$ID"
expect "Delete the todo" "200|204"

request GET "$BASE_URL$API_PATH/$ID"
expect "Deleted todo is gone" "404"

echo
if [ "$FAILED" -eq 0 ]; then
  echo "✅ All API checks passed"
else
  echo "❌ Some API checks failed"
fi
exit $FAILED