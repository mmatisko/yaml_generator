#!/bin/bash
command="ansible-playbook -bK -i hosts site.yml"

if [ "$1" = "--dry" ] || [ "$2" = "--dry" ]; then
  command+=" --check"
fi
if [ "$1" = "--debug" ] || [ "$2" = "--debug" ]; then
  command+=" -vvvv"
fi

echo "Evaluating command: $command"
eval $command
