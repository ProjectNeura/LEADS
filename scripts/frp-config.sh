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

require_argument() {
  if [ -n "$1" ];
  then echo "$1"
  else abort "Required argument $2 does not exist"
  fi
}

argument_exists_or() {
  if [ -n "$1" ];
  then echo "$1"
  else echo "$2"
  fi
}
if ! test -d "/usr/local/frp";
then abort "frp not found"
fi
echo "Configuring client..."
echo "serverAddr = \"$(require_argument "$1" "frp server IP")\"" > "/usr/local/frp/frpc.toml"
{
  echo "serverPort = $(argument_exists_or "$3" "7000")"
  echo "auth.method = \"token\""
  echo "auth.token = \"$(require_argument "$2" "frp token")\""
  echo "[[proxies]]"
  echo "name = \"leads-vec-comm\""
  echo "type = \"tcp\""
  echo "localIP = \"127.0.0.1\""
  echo "localPort = \"$(argument_exists_or "$4" "16900")\""
  echo "remotePort = \"$(argument_exists_or "$4" "16900")\""
  echo "name = \"leads-vec-rc\""
  echo "type = \"http\""
  echo "localIP = \"127.0.0.1\""
  echo "localPort = 8000"
  echo "customDomains = [\"$(argument_exists_or "$5" "leads-proxy.projectneura.org")\"]"
} >> "/usr/local/frp/frpc.toml"
echo "Configuring server..."
echo "bindPort = $(argument_exists_or "$3" "7000")" > "/usr/local/frp/frps.toml"
{
  echo "auth.method = \"token\""
  echo "auth.token = \"$(require_argument "$2" "frp token")\""
  echo "vhostHTTPPort = 80"
  echo "vhostHTTPSPort = 443"
} >> "/usr/local/frp/frps.toml"