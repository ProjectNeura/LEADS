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

echo "Downloading the script..."
execute_root "wget" "-O" "gstreamer-run.sh" "https://raw.githubusercontent.com/ProjectNeura/LEADS/main/scripts/gstreamer-run.sh"
echo "Moving the script to /usr/local/leads..."
execute_root "chmod" "755" "/usr/local/leads/gstreamer-run.sh"
execute_root "mv" "gstreamer-run.sh" "/usr/local/leads/gstreamer-run.sh"
execute_root "echo" "[Unit]" > "/home/$(logname)/.config/systemd/user/gstreamer.service"
{
  execute_root "echo" "Description=GStreamer"
  execute_root "echo" "After=graphical-session.target"
  execute_root "echo" "[Service]"
  execute_root "echo" "Type=simple"
  execute_root "echo" "ExecStart=/bin/bash /usr/local/leads/gstreamer-run.sh $0 $1 $2 $3"
  execute_root "echo" "Restart=always"
  execute_root "echo" "RestartSec=1s"
  execute_root "echo" "[Install]"
  execute_root "echo" "WantedBy=default.target"
} >> "/home/$(logname)/.config/systemd/user/gstreamer.service"
execute_root "chmod" "777" "/home/$(logname)/.config/systemd/user/default.target.wants"