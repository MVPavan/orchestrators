#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 prepare|verify" >&2
  exit 64
}

[[ $# -eq 1 ]] || usage
mode="$1"
[[ "$mode" == prepare || "$mode" == verify ]] || usage

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(git -C "$script_dir" rev-parse --show-toplevel)"
canonical="$script_dir/fixture"
patch="$script_dir/synthetic-change.patch"
manifest="$script_dir/fixture-manifest.sha256"
manifest_digest_file="$script_dir/fixture-manifest.digest"
output_root="$repo_root/scratchpad/code-intelligence/fixtures"
fixed_date="2026-07-24T00:00:00Z"
lanes=(codegraph cbm graphify)

canonical_manifest() {
  (
    cd "$canonical"
    find . -type f -print0 |
      LC_ALL=C sort -z |
      while IFS= read -r -d '' file; do
        sha256sum "${file#./}"
      done
    sha256sum "$patch" |
      sed 's#  .*#  synthetic-change.patch#'
  )
}

verify_manifest() {
  local candidate
  candidate="$(mktemp)"
  trap 'rm -f "$candidate"' RETURN
  canonical_manifest > "$candidate"
  diff -u "$manifest" "$candidate"
  test "$(sha256sum "$manifest" | cut -d ' ' -f 1)" = \
    "$(tr -d '\n' < "$manifest_digest_file")"
}

prepare_lane() {
  local lane="$1"
  local target="$output_root/$lane"
  if [[ -e "$target" ]]; then
    echo "refusing to replace existing fixture: $target" >&2
    exit 73
  fi

  mkdir -p "$target"
  cp -a "$canonical/." "$target/"
  cp "$patch" "$target/synthetic-change.patch"
  cp "$manifest" "$target/.fixture-source.sha256"
  cp "$manifest_digest_file" "$target/.fixture-manifest.digest"

  (
    cd "$target"
    sha256sum -c .fixture-source.sha256
    git init -q -b main --object-format=sha1
    git config user.name "Capability Fixture"
    git config user.email "fixture@invalid.local"
    git config commit.gpgsign false
    git config core.hooksPath /dev/null
    git add -- .
    GIT_AUTHOR_DATE="$fixed_date" GIT_COMMITTER_DATE="$fixed_date" \
      git commit -q -m "freeze mixed TypeScript Rust capability fixture"
    test -z "$(git status --porcelain=v1 --untracked-files=all)"
    git rev-parse HEAD > .git/fixture-commit
  )
}

verify_lane() {
  local lane="$1"
  local target="$output_root/$lane"
  test -d "$target/.git"
  (
    cd "$target"
    sha256sum -c .fixture-source.sha256
    test "$(tr -d '\n' < .fixture-manifest.digest)" = \
      "$(tr -d '\n' < "$manifest_digest_file")"
    test "$(git rev-parse --show-object-format)" = sha1
    test -z "$(git status --porcelain=v1 --untracked-files=all)"
    test "$(git rev-parse HEAD)" = "$(cat .git/fixture-commit)"
    git apply --check synthetic-change.patch
  )
}

verify_manifest

if [[ "$mode" == prepare ]]; then
  mkdir -p "$output_root"
  for lane in "${lanes[@]}"; do
    prepare_lane "$lane"
  done
fi

for lane in "${lanes[@]}"; do
  verify_lane "$lane"
done

reference="$output_root/${lanes[0]}"
for lane in "${lanes[@]:1}"; do
  diff -qr --exclude=.git "$reference" "$output_root/$lane"
  test "$(git -C "$reference" rev-parse HEAD)" = \
    "$(git -C "$output_root/$lane" rev-parse HEAD)"
done

printf 'fixture_manifest_sha256=%s\n' "$(tr -d '\n' < "$manifest_digest_file")"
printf 'fixture_commit=%s\n' "$(git -C "$reference" rev-parse HEAD)"
