#!/bin/sh

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

if ! command -v curl &> /dev/null;
then
  echo "cURL is not available, installing..."
  execute_root "apt" "install" "-y" "curl"
fi
latest_release=$(curl -s "https://api.github.com/repos/fatedier/frp/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")' | cut -c 2-)
if [ -z "$latest_release" ];
then abort "Failed to retrieve the latest release"
fi
echo "Downloading frp@${latest_release}..."
execute_root "wget" "-O" "frp.tar.gz" "https://github.com/fatedier/frp/releases/download/v${latest_release}/frp_${latest_release}_linux_amd64.tar.gz"
echo "Extracting..."
execute_root "tar" "-xzvf" "frp.tar.gz"
echo "Moving frp_${latest_release}_linux_amd64 to /usr/local/frp..."
execute_root "mv" "frp_${latest_release}_linux_amd64" "/usr/local/frp"
echo "Cleaning up..."
execute_root "rm" "frp.tar.gz" "frp_${latest_release}_linux_amd64"