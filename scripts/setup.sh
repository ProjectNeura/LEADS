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
execute "pip-leads" "install" "Pillow" "PySDL2" "customtkinter" "gpiozero" "lgpio" "pynmea2" "pynput" "pysdl2-dll" "pyserial" "leads"
echo "Creating Shortcut..."
echo "#!/bin/sh" > "/bin/leads-vec"
echo 'python-leads -m leads_vec "$@"' >> "/bin/leads-vec"
execute_root "chmod" "+x" "/bin/leads-vec"
echo "Verifying..."
execute "leads-vec" "info"