#!/bin/bash

if [ ! -r "/usr/local/leads/config.json" ]
then
  echo "Error: Config file does not exist"
  exit 1
fi
while ! xhost >& /dev/null
do sleep 1
done
# configure xws
/usr/bin/xhost +SI:localuser:"$USERNAME"
# change the interpreter or adjust the arguments according to your needs
python-leads -m leads_vec -c /usr/local/leads/config.json run