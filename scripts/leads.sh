#!/bin/sh

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

execute() {
  if ! "$@";
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute "/usr/local/leads/venv/bin/python" "-m" "leads_vec" "-c" "/usr/local/leads/config.json" "$@" "run"