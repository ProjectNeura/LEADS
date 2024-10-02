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
execute_root "pip-leads" "install" '"leads[vec]"'
echo "Creating executable entries..."
execute_root "echo" "#!/bin/bash" > "/bin/leads-vec"
execute_root "echo" 'python-leads -m leads_vec "$@"' >> "/bin/leads-vec"
execute_root "chmod" "+x" "/bin/leads-vec"
execute_root "echo" "#!/bin/bash" > "/bin/leads-vec-rc"
execute_root "echo" 'python-leads -m leads_vec_rc "$@"' >> "/bin/leads-vec-rc"
execute_root "chmod" "+x" "/bin/leads-vec-rc"
execute_root "echo" "#!/bin/bash" > "/bin/leads-vec-dp"
execute_root "echo" 'python-leads -m leads_vec_dp "$@"' >> "/bin/leads-vec-dp"
execute_root "chmod" "+x" "/bin/leads-vec-dp"
echo "Verifying..."
execute "leads-vec" "info"