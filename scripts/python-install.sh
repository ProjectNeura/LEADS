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

echo "Adding APT repository..."
execute_root "add-apt-repository" "ppa:deadsnakes/ppa"
execute_root "apt" "update"
echo "Installing Python 3.12..."
execute_root "apt" "install" "-y" "gcc" "python3.12" "python3.12-dev" "python3.12-venv"
echo "Installing Tcl/Tk..."
execute_root "apt" "install" "-y" "python3.12-tk"
echo "Creating Virtual Environment..."
execute_root "python3.12" "-m" "venv" "/usr/local/leads/venv"
echo "Creating Soft Links..."
echo "#!/bin/sh" > "/bin/python-leads"
echo '/usr/local/leads/venv/bin/python "$@"' >> "/bin/python-leads"
execute_root "ln" "-s" "/usr/local/leads/venv/bin/pip" "/bin/pip-leads"