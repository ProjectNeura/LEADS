if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo su
./python-install.sh
python3.12 -m pip install Pillow customtkinter keyboard pyserial leads
python3.12 -m leads_vec info