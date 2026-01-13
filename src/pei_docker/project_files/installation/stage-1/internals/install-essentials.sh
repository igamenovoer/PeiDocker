#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# install these anyway
# apt update
# apt-get install --reinstall -y ca-certificates

# if WITH_ESSENTIAL_APPS is false or not set, exit
if [ "$WITH_ESSENTIAL_APPS" != "true" ]; then
  exit 0
fi

# apt-get install sudo nano mc ne software-properties-common -y
apt-get install sudo nano micro -y
apt-get install git net-tools curl tmux unzip -y
# apt-get install build-essential cmake pkg-config -y

# if ssh server is not installed, install it
dpkg -l | grep openssh-server
if [ $? -eq 0 ]; then
  echo "openssh-server is already installed"
else
  echo "openssh-server is not installed, installing..."
  apt-get install openssh-server -y
fi

# for automation
echo "Installing sshpass for automation..."
apt-get install sshpass -y