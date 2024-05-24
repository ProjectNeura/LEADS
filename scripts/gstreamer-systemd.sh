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
execute_root "mv" "gstreamer-run.sh" "/usr/local/leads/gstreamer-run.sh"
execute_root "echo" "[Unit]" > "/home/$(logname)/.config/systemd/user/gstreamer.service"
{
  execute_root "echo" "Description=GStreamer"
  execute_root "echo" "After=graphical-session.target"
  execute_root "echo" "[Service]"
  execute_root "echo" "Type=simple"
  execute_root "echo" "ExecStart=/bin/bash /usr/local/leads/gstreamer-run.sh $0 $1 $2 $3"
  execute_root "echo" "type = \"tcp\""
  execute_root "echo" "localIP = \"127.0.0.1\""
  execute_root "echo" "localPort = $(argument_exists_or "$4" "16900")"
  execute_root "echo" "remotePort = $(argument_exists_or "$4" "16900")"
} >> "/home/$(logname)/.config/systemd/user/gstreamer.service"