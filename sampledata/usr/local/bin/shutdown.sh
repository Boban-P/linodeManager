#!/bin/bash

if [[ -f /vars.sh ]]; then
    source /vars.sh
fi

project=${project:-""}
user=${user:-""}
backupFile=${backupFile:-""}
restoreFile=${restoreFile:-""}
bucket=${bucket:-""}

su --login "${user}" -c "cloudscript ${project} startall.sh stopall"
cd /home

mkdir /home/user
chown "${user}:${user}" /home/user

for file in .ssh .local bin dockerscript/Packages/${project//:/\/}/Assets; do
    mkdir -p "$(dirname "/home/user/${file}")"
    cp -a "/home/${user}/${file}" "/home/user/${file}"
done

tar -cJf "${restoreFile}" user
s3cmd put "${restoreFile}" "s3://${bucket}"
