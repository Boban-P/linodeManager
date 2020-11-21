#!/bin/bash

if [[ -f /vars.sh ]]; then
    source /vars.sh
fi

project=${project:-""}
user=${user:-""}
sitename="${subDomain}.${domain}"

su --login "${user}" -c "cloudscript ${project} build_image"
su --login "${user}" -c "cloudscript ${project} startall.sh start --ip \$(private_ip) --public \$(public_ip) --sitename ${sitename}"
sleep 20
su --login "${user}" -c "cloudscript ${project} balancer apachectl graceful"
