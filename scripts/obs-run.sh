if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo MESA_GL_VERSION_OVERRIDE=3.3 obs