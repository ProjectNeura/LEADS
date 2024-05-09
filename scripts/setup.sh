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

echo "Installing Python..."
execute_root "wget" "-O" "python-install.sh" "https://raw.githubusercontent.com/ProjectNeura/LEADS/master/scripts/python-install.sh"
execute_root "/bin/sh" "python-install.sh"
echo "Cleaning up..."
execute_root "rm" "python-install.sh"
echo "Installing dependencies..."
execute "python3.12" "-m" "pip" "install" "Pillow" "PySDL2" "customtkinter" "gpiozero" "lgpio" "pynmea2" "pynput" "pysdl2-dll" "pyserial" "leads"
execute "python3.12" "-m" "leads_vec" "info"