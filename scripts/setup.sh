abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if (( EUID ));
then abort "Error: This script requires root permission"
fi

execute() {
  if ! "sudo" "$@";
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

echo "Installing Python..."
execute "wget" "https://raw.githubusercontent.com/ProjectNeura/LEADS/master/scripts/python-install.sh"
execute "/bin/sh" "python-install.sh"
echo "Cleaning up..."
execute "rm" "python-install.sh*"
echo "Installing dependencies..."
execute "python3.12" "-m" "pip" "install" "Pillow" "customtkinter" "pynput" "pyserial" "lgpio" "gpiozero" "pynmea2" "leads"
execute "python3.12" "-m" "leads_vec" "info"