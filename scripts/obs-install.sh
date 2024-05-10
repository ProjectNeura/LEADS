#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if [ "${EUID:-$(id -u)}" -ne 0 ];
then abort "Error: This script requires root permission"
fi

execute() {
  if ! "$@";
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute_root() {
  execute "sudo" "$@"
}

echo "Adding APT repository..."
execute_root "add-apt-repository" "ppa:obsproject/obs-studio"
execute_root "apt" "update"
echo "Installing OBS Studio..."
execute_root "apt" "-y" "install" "ffmpeg" "obs-studio"