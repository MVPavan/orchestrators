#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
updater="$script_dir/sync-submodules.sh"

if [[ ! -x "$updater" ]]; then
  echo "expected executable updater at $updater" >&2
  exit 1
fi

temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT

make_upstream() {
  local name=$1
  local source="$temp_dir/$name-source"
  local bare="$temp_dir/$name.git"

  git init --quiet "$source"
  git -C "$source" config user.name Test
  git -C "$source" config user.email test@example.com
  printf 'one\n' >"$source/$name.txt"
  git -C "$source" add "$name.txt"
  git -C "$source" commit --quiet -m initial
  git -C "$source" branch -M main
  git init --bare --quiet "$bare"
  git -C "$source" remote add origin "$bare"
  git -C "$source" push --quiet -u origin main
}

advance_upstream() {
  local name=$1
  local source="$temp_dir/$name-source"

  printf 'two\n' >>"$source/$name.txt"
  git -C "$source" commit --quiet -am advance
  git -C "$source" push --quiet
}

make_upstream alpha
make_upstream beta

parent="$temp_dir/parent"
git init --quiet "$parent"
git -C "$parent" config user.name Test
git -C "$parent" config user.email test@example.com
touch "$parent/README.md"
git -C "$parent" add README.md
git -C "$parent" commit --quiet -m initial
git -C "$parent" -c protocol.file.allow=always submodule add --quiet -b main "$temp_dir/alpha.git" external/alpha
git -C "$parent" -c protocol.file.allow=always submodule add --quiet -b main "$temp_dir/beta.git" external/beta
git -C "$parent" add .gitmodules external/alpha external/beta
git -C "$parent" commit --quiet -m add-submodules

mkdir -p "$parent/external"
cp "$updater" "$parent/external/sync-submodules.sh"
chmod +x "$parent/external/sync-submodules.sh"

advance_upstream alpha
advance_upstream beta

before_alpha=$(git -C "$parent/external/alpha" rev-parse HEAD)
before_beta=$(git -C "$parent/external/beta" rev-parse HEAD)

dry_run=$(cd "$parent" && external/sync-submodules.sh --dry-run)
[[ "$dry_run" == *"would update external/alpha"* ]]
[[ "$dry_run" == *"would update external/beta"* ]]
[[ $(git -C "$parent/external/alpha" rev-parse HEAD) == "$before_alpha" ]]
[[ $(git -C "$parent/external/beta" rev-parse HEAD) == "$before_beta" ]]

(cd "$parent" && external/sync-submodules.sh)
[[ $(git -C "$parent/external/alpha" rev-parse HEAD) != "$before_alpha" ]]
[[ $(git -C "$parent/external/beta" rev-parse HEAD) != "$before_beta" ]]
git -C "$parent" diff --cached --quiet
[[ $(git -C "$parent" diff --name-only -- external/alpha external/beta) == $'external/alpha\nexternal/beta' ]]

git -C "$parent" add external/alpha external/beta
git -C "$parent" commit --quiet -m update-submodules
advance_upstream alpha
advance_upstream beta
printf 'local change\n' >>"$parent/external/beta/beta.txt"
blocked_alpha=$(git -C "$parent/external/alpha" rev-parse HEAD)

if (cd "$parent" && external/sync-submodules.sh); then
  echo "expected dirty-submodule preflight to fail" >&2
  exit 1
fi

[[ $(git -C "$parent/external/alpha" rev-parse HEAD) == "$blocked_alpha" ]]
echo "sync-submodules test: PASS"
