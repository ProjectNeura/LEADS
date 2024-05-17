#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if test ! -d "/usr/local/frp"
then abort "Error: /usr/local/frp not found"
fi

execute() {
  if ! "$@"
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute_root() {
  execute "sudo" "$@"
}

require_argument() {
  if test -z "$1"
  then abort "Error: Required argument $2 does not exist"
  else echo "$1"
  fi
}

argument_exists_or() {
  if test -z "$1"
  then echo "$2"
  else echo "$1"
  fi
}

echo "Configuring client..."
execute_root "echo" "serverAddr = \"$(require_argument "$1" "frp_server_ip")\"" > "/usr/local/frp/frpc.toml"
{
  execute_root "echo" "serverPort = $(argument_exists_or "$3" "7000")"
  execute_root "echo" "auth.method = \"token\""
  execute_root "echo" "auth.token = \"$(require_argument "$2" "frp_token")\""
  execute_root "echo" "[[proxies]]"
  execute_root "echo" "name = \"leads-vec-comm\""
  execute_root "echo" "type = \"tcp\""
  execute_root "echo" "localIP = \"127.0.0.1\""
  execute_root "echo" "localPort = $(argument_exists_or "$4" "16900")"
  execute_root "echo" "remotePort = $(argument_exists_or "$4" "16900")"
} >> "/usr/local/frp/frpc.toml"
echo "Configuring server..."
execute_root "echo" "bindPort = $(argument_exists_or "$3" "7000")" > "/usr/local/frp/frps.toml"
{
  execute_root "echo" "auth.method = \"token\""
  execute_root "echo" "auth.token = \"$(require_argument "$2" "frp_token")\""
  execute_root "echo" "vhostHTTPPort = 80"
  execute_root "echo" "vhostHTTPSPort = 443"
} >> "/usr/local/frp/frps.toml"