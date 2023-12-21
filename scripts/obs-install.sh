if ! sudo -v &>/dev/null;
then
  echo "the script requires sudo"
  exit 1
fi
add-apt-repository ppa:obsproject/obs-studio
apt update
apt install ffmpeg obs-studio