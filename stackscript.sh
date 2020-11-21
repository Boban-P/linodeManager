#!/bin/bash
# <UDF name="user" label="default username for non root user" default="worker" example="developer, guest etc." />
# <UDF name="bucket" label="linode object storage bucket name" example="create a bucket in object storage" />
# <UDF name="accessKey" label="Access key for linode object storage" example="create from linode object storage" />
# <UDF name="secretKey" label="Secret key for linode object storage" example="create from linode object storage" />
# <UDF name="systemBackup" label="name of system backup file" default="system.tar.xz" example="it should be .tar.xz extracted to root of filesystem" />
# <UDF name="backupFile" label="name of application backup file" default="user.tar.xz" example="it should be .tar.xz extracted to users home directory" />
# <UDF name="restoreFile" label="filename to save data before shutting down the server" example="it should be .tar.xz created from users home directory" />
# <UDF name="repourl" label="repository url to configure app system" example="a remotely accessible git repo" />
# <UDF name="repobranch" label="the branch name of repository to start the repository" default="development" example="main, staging, development, testing, production etc" />
# <UDF name="reponame" label="name of directory the repo needs to clone to" example="the last part of repourl without .git" />
# <UDF name="project" label="name of project the server needs to run on" example="cloudscript project url" />
# <UDF name="domain" label="domain to set records into" example="must be a domain owned in linode" />
# <UDF name="subDomain" label="subdomain to which to set dns records to, unused" example="anything" />

cd
restoreFile=${restoreFile//default/}
subDomain=${subDomain//default/}
user="${user}1"

restoreFile=${restoreFile:-"${LINODE_ID}.${backupFile}"}
subDomain=${subDomain:-${LINODE_ID}}
linode_datacenter='ap-south-1'

# store variables to vars file.
echo "
user=${user}
bucket=${bucket}
systemBackup=${systemBackup}
backupFile=${backupFile}
restoreFile=${restoreFile}
repourl=${repourl}
repobranch=${repobranch}
project=${project}
domain=${domain}
subDomain=${subDomain}
" >/vars.sh
chmod 600 /vars.sh

# backport for s3cmd
echo "deb https://deb.debian.org/debian buster-backports main" >>/etc/apt/sources.list
/usr/bin/apt-get update
/usr/bin/apt-get install -y shorewall shorewall6 git
/usr/bin/apt-get install -t buster-backports -y s3cmd
# configure s3cmd
echo "${accessKey}
${secretKey}
SG
${linode_datacenter}.linodeobjects.com
%(bucket)s.${linode_datacenter}.linodeobjects.com
asdf




Y
Y
" | s3cmd --configure
sed -i 's/^website_endpoint.*$/website_endpoint = http:\/\/%(bucket)s.website-'${linode_datacenter}'.linodeobjects.com/' .s3cfg

# create a user.
useradd -m -s /bin/bash "${user}"

# configure system & firewall
mkdir tmp
s3cmd get "s3://${bucket}/${systemBackup}" ./
tar -xJf "${systemBackup}" -C tmp
cp -a tmp/* /
rm -rf tmp
systemctl enable shorewall shorewall6
systemctl start shorewall shorewall6

cd /home/${user}

mkdir tmp
s3cmd get "s3://${bucket}/${backupFile}" ./
tar -xJf "${backupFile}" -C tmp
mv tmp/user "tmp/${user}"
cp -a tmp/* ../
rm -rf tmp
mv "${reponame}" "${reponame}.backup"
# create repository
su --login "${user}" -c "git clone --dept 1 ${repourl} -b ${repobranch} ${reponame}"
cp -a "${reponame}.backup"/* "${reponame}/"

apt-get install -y docker.io
addgroup "${user}" docker
systemctl enable startserver.service
systemctl start startserver.service

env >/env.info
