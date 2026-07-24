#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <lane> <command> [args...]" >&2
  exit 64
}

[[ $# -ge 2 ]] || usage

lane="$1"
shift

if [[ ! "$lane" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "lane must match [a-z0-9][a-z0-9-]*" >&2
  exit 64
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"
runtime_root="$repo_root/scratchpad/code-intelligence/runtime"
lane_root="$runtime_root/lanes/$lane"

# A caller may explicitly add a runtime directory (for example, a tool-local
# Node.js bin directory). Nothing else from the caller's PATH is inherited.
base_path="$(getconf PATH 2>/dev/null || printf '%s' '/usr/bin:/bin')"
if [[ -n "${CODE_INTEL_EXTRA_PATH:-}" ]]; then
  child_path="${CODE_INTEL_EXTRA_PATH}:$base_path"
else
  child_path="$base_path"
fi

umask 077
mkdir -p \
  "$lane_root/home" \
  "$lane_root/cache" \
  "$lane_root/config/codex" \
  "$lane_root/config/claude" \
  "$lane_root/data" \
  "$lane_root/state" \
  "$lane_root/tmp" \
  "$lane_root/output" \
  "$lane_root/cbm-cache" \
  "$lane_root/uv-cache"

cd "$repo_root"

# env -i prevents inherited provider credentials and unrelated tool settings.
# The offline flags stop supported package/model clients from going online,
# but they are not a kernel-level network sandbox. The current host does not
# permit unshare(1) or bubblewrap network namespaces, so callers must treat
# network absence as an audited policy rather than an enforced guarantee.
exec env -i \
  PATH="$child_path" \
  HOME="$lane_root/home" \
  XDG_CACHE_HOME="$lane_root/cache" \
  XDG_CONFIG_HOME="$lane_root/config" \
  XDG_DATA_HOME="$lane_root/data" \
  XDG_STATE_HOME="$lane_root/state" \
  TMPDIR="$lane_root/tmp" \
  CODEX_HOME="$lane_root/config/codex" \
  CLAUDE_CONFIG_DIR="$lane_root/config/claude" \
  CBM_CACHE_DIR="$lane_root/cbm-cache" \
  GRAPHIFY_OUT="$lane_root/output/graphify-out" \
  UV_CACHE_DIR="$lane_root/uv-cache" \
  UV_OFFLINE=1 \
  PIP_NO_INDEX=1 \
  PIP_CONFIG_FILE=/dev/null \
  npm_config_offline=true \
  npm_config_audit=false \
  npm_config_fund=false \
  NPM_CONFIG_USERCONFIG=/dev/null \
  HF_HUB_OFFLINE=1 \
  TRANSFORMERS_OFFLINE=1 \
  DO_NOT_TRACK=1 \
  OTEL_SDK_DISABLED=true \
  GRAPHIFY_TELEMETRY_DISABLED=1 \
  GIT_CONFIG_NOSYSTEM=1 \
  GIT_CONFIG_GLOBAL=/dev/null \
  GIT_CONFIG_COUNT=2 \
  GIT_CONFIG_KEY_0=credential.helper \
  GIT_CONFIG_VALUE_0= \
  GIT_CONFIG_KEY_1=credential.interactive \
  GIT_CONFIG_VALUE_1=false \
  GIT_TERMINAL_PROMPT=0 \
  GIT_ASKPASS=/bin/false \
  GCM_INTERACTIVE=never \
  CI=1 \
  NO_COLOR=1 \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  "$@"
