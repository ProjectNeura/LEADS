if ! sudo -v &>/dev/null;
then
  echo "the script requires sudo"
  exit 1
fi
sudo su
apt update
apt install python3.11