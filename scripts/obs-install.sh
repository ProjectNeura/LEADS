if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo su
add-apt-repository ppa:obsproject/obs-studio
apt update
apt install ffmpeg obs-studio