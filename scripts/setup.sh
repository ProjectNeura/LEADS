if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo su
./python-install.sh
python3.11 -m pip install pysimplegui keyboard RPi.GPIO pyserial leads
python3.11 -m leads_vec info