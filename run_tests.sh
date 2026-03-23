#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "== Backend tests =="
(cd BACKEND-CHATBOT-SDS && bash run_tests.sh)

echo "== Frontend tests =="
(cd FRONTEND-CHATBOT-SDS && bash run_tests.sh)

echo "All tests passed."
