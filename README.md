# Registration Server

# Overview

This Registration Server allows for the allocation of secure subdomains 
that self-generate SSL certificates
This server utilizes three main applications to allow for this to occur.
- PowerDNS
- Pagekite
- WebthingsIO Registration Server

## Installation
To correctly install and configure this webserver, a plethroa of actions 
must first occur.
Spin up an image of Ubuntu 20.04, update and upgrade
```
sudo apt update && sudo apt upgrade

sudo apt-get install \
ca-certificates \
curl \
gnupg \
Lsb-release
```
Install Docker
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg 
--dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) 
signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] 
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | 
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
Install Nginx and SQLite
```
sudo apt install nginx
sudo apt install sqlite3
```
Clone the Registration Server's GIT repository and build a docker image
```
git clone https://github.com/WebThingsIO/registration_server.git
cd registration_server
sudo docker build --build-arg "db_type=sqlite" -t registration-server
```
Create directories for configuration and data shares
```
mkdir /opt/docker/
chmod 777 /opt/docker
mkdir /opt/docker/registration-server
mkdir /opt/docker/registration-server/data
mkdir /opt/docker/registration-server/config
```
Create a blank SQLite database
```
cd /opt/docker/registration-server/data
Sqlite3 domains.sqlite
sqlite> ;
```
Now three configuration files utilized by the Registration Server must 
be moved to the config directory
```
mv /Path/to/file/config.toml /opt/docker/registration-server/config
mv /Path/to/file/pdns.conf /opt/docker/registration-server/config
mv /Path/to/file/pagekite.conf /opt/docker/registration-server/config
```
These configuration files will need to be changed to reflect your domain 
environment

Nginx will need to be configured to serve the Registration Server's API 
endpoints and allow tunneling throuh the domain
```
mv /path/to/nginx.conf /etc/nginx/
sudo rm /etc/nginx/sites-enabled/default
sudo mkdir /etc/pki/nginx
openssl dhparam -out /etc/pki/nginx/dhparams.pem 2048
```
The nginx.conf file will need to also be configured to reflect your 
domain environment

port 53 must be opened for the Registration Server
```
Sudo systemctl stop systemd-resolved
Sudo nano /etc/systemd/resolved.conf
```
Uncomment DNS in the resolve section and append 8.8.8.8 after the = and 
change the DNSStubListener directive
```
DNS=8.8.8.8
DNSStubListener=no
```
Allow these changes to be effective to the system
```
sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl start systemd-resolved
```
Now the docker image is ready to run
```
sudo docker run -d -v 
/opt/docker/registration-server/config:/home/user/config -v 
/opt/docker/registration-server/data:/home/user/data -p 127.0.0.1:81:81 
-p 443:4443 -p 53:53  -p 53:53/udp --log-opt max-size=1m --log-opt 
max-file=10 --restart unless-stopped --name registration-server 
registration-server:latest
```
To check the status of this service and see errors produced 
```
sudo docker logs -f registration-server
```
Retrieve SSL certificates for the Nginx server by installing and using 
certbot
```
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot certonly --nginx
```

