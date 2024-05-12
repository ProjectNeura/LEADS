#!/bin/bash

if test ! -r "/usr/local/leads/config.json"
then
  printf "Error: Config file does not exist or not readable\n" >&2
  exit 1
fi
# change the interpreter or adjust the arguments according to your needs
python-leads -m leads_vec -c /usr/local/leads/config.json run