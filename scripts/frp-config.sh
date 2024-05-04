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

argument_exists_or() {
  if [ -n "$1" ];
  then
    echo "$1"
  else
    echo "$2"
  fi
}
if test -d "/usr/local/frp";
then
  abort "frp is not installed yet"
fi
echo "Configuring client..."
execute_root "echo" "serverAddr = \"$1\"" ">" "/usr/local/frp/frpc.toml"
execute_root "echo" "serverPort = $(argument_exists_or "$3" "7000")" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "auth.method = \"token\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "auth.token = \"$2\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "[[proxies]]" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "name = \"leads-vec-comm\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "type = \"tcp\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "localIP = \"127.0.0.1\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "localPort = \"$(argument_exists_or "$4" "16900")\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "remotePort = \"$(argument_exists_or "$4" "16900")\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "name = \"leads-vec-rc\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "type = \"http\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "localIP = \"127.0.0.1\"" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "localPort = 8000" ">>" "/usr/local/frp/frpc.toml"
execute_root "echo" "customDomains = [\"$(argument_exists_or "$5" "leads-proxy.projectneura.org")\"]" ">>" "/usr/local/frp/frpc.toml"
echo "Configuring server..."
execute_root "echo" "bindPort = $(argument_exists_or "$3" "7000")" ">>" "/usr/local/frp/frps.toml"
execute_root "echo" "auth.method = \"token\"" ">>" "/usr/local/frp/frps.toml"
execute_root "echo" "auth.token = \"$2\"" ">>" "/usr/local/frp/frps.toml"
execute_root "echo" "vhostHTTPPort = 80" ">>" "/usr/local/frp/frps.toml"
execute_root "echo" "vhostHTTPSPort = 443" ">>" "/usr/local/frp/frps.toml"