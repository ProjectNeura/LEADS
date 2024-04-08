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

echo "Adding APT repository..."
execute "add-apt-repository" "ppa:deadsnakes/ppa"
execute "apt" "update"
echo "Installing Python 3.12..."
execute "apt" "install" "-y" "python3.12"
echo "Fixing Pip..."
execute "wget" "https://bootstrap.pypa.io/get-pip.py"
execute "python3.12" "get-pip.py"
echo "Cleaning up..."
execute "rm" "get-pip.py"
echo "Installing Tcl/Tk..."
execute "apt" "install" "-y" "python3.12-tk"