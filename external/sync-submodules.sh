#!/usr/bin/env bash
# Update configured external submodules by direct checkout only.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: external/sync-submodules.sh [--dry-run] [external/submodule-path ...]

Fetch each selected submodule's configured branch and directly check out its
latest origin commit. This script never merges, rebases, forces, stages,
commits, or pushes. It refuses to update if any selected submodule is dirty
or uninitialized.
EOF
}

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(git -C "$script_dir/.." rev-parse --show-toplevel)
gitmodules="$repo_root/.gitmodules"
dry_run=false

if [[ ! -f "$gitmodules" ]]; then
  echo "missing .gitmodules at repository root" >&2
  exit 1
fi

while (($#)); do
  case "$1" in
    --dry-run) dry_run=true ;;
    -h|--help) usage; exit 0 ;;
    --*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *) break ;;
  esac
  shift
done

configured_paths=()
while read -r _ path; do
  configured_paths+=("$path")
done < <(git config --file "$gitmodules" --get-regexp '^submodule\..*\.path$')

if ((${#configured_paths[@]} == 0)); then
  echo "no configured submodules" >&2
  exit 1
fi

selected_paths=("$@")
if ((${#selected_paths[@]} == 0)); then
  selected_paths=("${configured_paths[@]}")
fi

contains_configured_path() {
  local candidate=$1 path
  for path in "${configured_paths[@]}"; do
    [[ "$path" == "$candidate" ]] && return 0
  done
  return 1
}

submodule_name_for_path() {
  local wanted_path=$1 key name path
  while read -r key path; do
    if [[ "$path" == "$wanted_path" ]]; then
      name=${key#submodule.}
      printf '%s\n' "${name%.path}"
      return 0
    fi
  done < <(git config --file "$gitmodules" --get-regexp '^submodule\..*\.path$')
  return 1
}

# Preflight every requested path before fetching or changing any checkout.
for path in "${selected_paths[@]}"; do
  if [[ "$path" != external/* ]] || ! contains_configured_path "$path"; then
    echo "not a configured external submodule: $path" >&2
    exit 1
  fi

  name=$(submodule_name_for_path "$path")
  branch=$(git config --file "$gitmodules" --get "submodule.$name.branch" || true)
  if [[ -z "$branch" ]]; then
    echo "no configured branch for $path" >&2
    exit 1
  fi

  submodule="$repo_root/$path"
  if ! git -C "$submodule" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "uninitialized submodule: $path" >&2
    exit 1
  fi
  if [[ -n $(git -C "$submodule" status --porcelain --untracked-files=all) ]]; then
    echo "dirty submodule: $path" >&2
    exit 1
  fi
done

changed_paths=()
for path in "${selected_paths[@]}"; do
  name=$(submodule_name_for_path "$path")
  branch=$(git config --file "$gitmodules" --get "submodule.$name.branch")
  submodule="$repo_root/$path"

  git -C "$submodule" fetch --quiet origin "refs/heads/$branch:refs/remotes/origin/$branch"
  target=$(git -C "$submodule" rev-parse --verify "refs/remotes/origin/$branch^{commit}")
  current=$(git -C "$submodule" rev-parse HEAD)

  if [[ "$current" == "$target" ]]; then
    printf 'up to date %s (%s)\n' "$path" "$target"
    continue
  fi

  if "$dry_run"; then
    printf 'would update %s: %s -> %s\n' "$path" "$current" "$target"
    continue
  fi

  git -C "$submodule" checkout --quiet --detach "$target"
  changed_paths+=("$path")
  printf 'updated %s: %s -> %s\n' "$path" "$current" "$target"
done

if "$dry_run"; then
  exit 0
fi

if ((${#changed_paths[@]} == 0)); then
  echo "no submodule pointers changed"
  exit 0
fi

echo
echo "Parent-repository Gitlink diff (not staged):"
git -C "$repo_root" diff --submodule=short -- "${changed_paths[@]}"
