#!/bin/bash
# ==================Config===================

# If the name of your evmos executable is not "evmosd" then change the setting below.
EXECUTABLE_EVMOS_FILE_NAME=evmosd

# ===========================================

EVMOSD_PATH=$(whereis $EXECUTABLE_EVMOS_FILE_NAME | grep -Po "(?<=$EXECUTABLE_EVMOS_FILE_NAME:\s).*")

if [ -z "$EVMOSD_PATH" ]
then
  echo "[ERROR] The executable file 'evmosd' is not found in the PATH variable. Add the location of this file to the PATH variable and restart the script."
  exit
fi

#Install docker and docker-compose
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo -ne '\n' | sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo "$UBUNTU_CODENAME") stable"
sudo apt update
sudo apt install -y docker-ce docker-compose
usermod -aG docker $USER

# turn on prometheus metrics
sed -i 's/prometheus = false/prometheus = true/g' $HOME/.evmosd/config/config.toml

# install variables
echo "Enter master server ip ( EXAMPLE: 127.0.0.1 )"
read MASTER_SERVER_IP

if [ -z "$MASTER_SERVER_IP" ]
then
  MASTER_SERVER_IP="127.0.0.1"
fi

# clear old settings
echo "" > settings.env

# create settings file
echo "MASTER_SERVER_IP=$MASTER_SERVER_IP" >> settings.env
echo "[INFO] MASTER_SERVER_IP set $MASTER_SERVER_IP"

PROMETHEUS_METRICS_PORT=$(cat $HOME/.evmosd/config/config.toml | grep -Po "(?<=prometheus_listen_addr = \":)[0-9]*")
echo "PROMETHEUS_METRICS_PORT=$PROMETHEUS_METRICS_PORT" >> settings.env
echo "[INFO] PROMETHEUS_METRICS_PORT set $PROMETHEUS_METRICS_PORT"

RPC_API_PORT=$(cat $HOME/.evmosd/config/app.toml | grep -Po "(?<=address = \"tcp://\d\.\d\.\d\.\d:)\d+")
echo "RPC_API_PORT=$RPC_API_PORT" >> settings.env
echo "[INFO] RPC_API_PORT set $RPC_API_PORT"

MONIKER=$(cat $HOME/.evmosd/config/config.toml | grep -Po "(?<=moniker = \")\w+")
echo "MONIKER=$MONIKER" >> settings.env
echo "[INFO] MONIKER set $MONIKER"

# Turn on RPC API
sed -i '104s/.*/enable = true/g' $HOME/.evmosd/config/app.toml

# setting up node viewer
echo "[INFO] Starting node viewer..."
docker-compose up -d --build
echo "[INFO] Node viewer is up!"

# print help info
IP=$(curl ifconfig.co)
echo "[INFO] Firewall reloaded successfully! Checking info on http://$IP:10100/metrics"
echo "[INFO] You can change any settings in settings.env file."
echo "[INFO] For apply your changes execute docker-compose up -d --build"

echo "[WARNING] --*Please restart your evmosd!*--"
