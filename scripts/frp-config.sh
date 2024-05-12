#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if test "${EUID:-$(id -u)}" -eq 0
then abort "Error: Do not execute this script as root"
fi

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
  then abort "Required argument $2 does not exist"
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
echo "serverAddr = \"$(require_argument "$1" "frp_server_ip")\"" > "/usr/local/frp/frpc.toml"
{
  echo "serverPort = $(argument_exists_or "$3" "7000")"
  echo "auth.method = \"token\""
  echo "auth.token = \"$(require_argument "$2" "frp_token")\""
  echo "[[proxies]]"
  echo "name = \"leads-vec-comm\""
  echo "type = \"tcp\""
  echo "localIP = \"127.0.0.1\""
  echo "localPort = $(argument_exists_or "$4" "16900")"
  echo "remotePort = $(argument_exists_or "$4" "16900")"
} >> "/usr/local/frp/frpc.toml"
echo "Configuring server..."
echo "bindPort = $(argument_exists_or "$3" "7000")" > "/usr/local/frp/frps.toml"
{
  echo "auth.method = \"token\""
  echo "auth.token = \"$(require_argument "$2" "frp_token")\""
  echo "vhostHTTPPort = 80"
  echo "vhostHTTPSPort = 443"
} >> "/usr/local/frp/frps.toml"