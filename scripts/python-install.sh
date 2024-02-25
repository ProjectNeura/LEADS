if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo su
add-apt-repository ppa:deadsnakes/ppa
apt update
apt install python3.12
wget https://bootstrap.pypa.io/get-pip.py
python3.12 get-pip.py
apt install python3.12-tk
apt install python3-rpi.gpio