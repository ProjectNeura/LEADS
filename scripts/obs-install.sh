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
execute "add-apt-repository" "ppa:obsproject/obs-studio"
execute "apt" "update"
echo "Installing OBS Studio..."
execute "apt" "-y" "install" "ffmpeg" "obs-studio"