#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if test "${EUID:-$(id -u)}" -eq 0
then abort "Error: Do not execute this script as root"
fi

execute() {
  if ! "$@"
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute_root() {
  execute "sudo" "$@"
}

execute_root "MESA_GL_VERSION_OVERRIDE=3.3" "obs"