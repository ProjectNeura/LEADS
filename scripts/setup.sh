#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

execute() {
  if ! "$@"
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute_root() {
  execute "sudo" "$@"
}

echo "Installing Python..."
execute_root "wget" "-O" "python-install.sh" "https://raw.githubusercontent.com/ProjectNeura/LEADS/main/scripts/python-install.sh"
execute_root "/bin/bash" "python-install.sh"
echo "Cleaning up..."
execute_root "rm" "python-install.sh"
echo "Installing dependencies..."
execute_root "pip-leads" "install" "Pillow" "PySDL2" "customtkinter" "gpiozero" "lgpio" "opencv-python-headless" "pynmea2" "pynput" "pysdl2-dll" "pyserial" "leads"
echo "Creating Shortcut..."
execute_root "echo" "#!/bin/bash" > "/bin/leads-vec"
execute_root "echo" 'python-leads -m leads_vec "$@"' >> "/bin/leads-vec"
execute_root "chmod" "+x" "/bin/leads-vec"
echo "Verifying..."
execute "leads-vec" "info"