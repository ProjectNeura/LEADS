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

export MESA_GL_VERSION_OVERRIDE=3.3
execute "obs"