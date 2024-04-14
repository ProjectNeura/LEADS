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
execute_root "apt" "install" "-y" "gcc" "python3.12" "python3.12-dev"
echo "Fixing Pip..."
execute_root "wget" "-O" "get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
execute_root "python3.12" "get-pip.py"
echo "Cleaning up..."
execute_root "rm" "get-pip.py"
echo "Installing Tcl/Tk..."
execute_root "apt" "install" "-y" "python3.12-tk"