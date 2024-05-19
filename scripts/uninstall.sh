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

ask() {
  printf "%s >>>" "$@" >&0
  read -r input
  echo "$input" | tr "[:upper:]" "[:lower:]"
}

if test -e "/home/$(logname)/.config/systemd/user/leads-vec.service"
then
  if systemctl --user is-enabled --quiet "leads-vec"
  then
    echo "Disabling Systemd service leads-vec..."
    execute_root "systemctl" "--user" "disable" "leads-vec"
  else echo "Systemd service leads-vec not enabled, skipping..."
  fi
  echo "Removing Systemd service leads-vec..."
  execute_root "rm" "/home/$(logname)/.config/systemd/user/leads-vec.service"
else echo "Systemd service leads-vec not detected, skipping..."
fi

if test -e "/usr/local/frp"
then
  if test "$(ask "Do you want to remove FRP? (Y/n)")" = "y"
  then
    echo "Removing FRP..."
    execute_root "rm" "-r" "/usr/local/frp"
  else echo "Abort"
  fi
else echo "FRP not detected, skipping..."
fi

if test -e "/usr/local/leads/config.json"
then
  if test "$(ask "Do you want to remove the configuration file? (Y/n)")" = "y"
  then execute_root "rm" "/usr/local/leads/config.json"
  else echo "Abort"
  fi
else echo "Configuration file not detected, skipping..."
fi

if test -e "/bin/leads-vec"
then
  echo "Removing soft link /bin/leads-vec..."
  execute_root "rm" "/bin/leads-vec"
else echo "Soft link /bin/leads-vec not detected, skipping..."
fi

if test -e "/bin/pip-leads"
then
  echo "Removing soft link /bin/pip-leads..."
  execute_root "rm" "/bin/pip-leads"
else echo "Soft link /bin/pip-leads not detected, skipping..."
fi

if test -e "/bin/python-leads"
then
  echo "Removing soft link /bin/python-leads..."
  execute_root "rm" "/bin/python-leads"
else echo "Soft link /bin/python-leads not detected, skipping..."
fi

if test -e "/usr/local/leads/venv"
then
  echo "Removing virtual environment..."
  execute_root "rm" "-r" "/usr/local/leads/venv"
else echo "Virtual environment not detected, skipping..."
fi

echo "LEADS has been uninstalled"