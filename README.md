### Self host in VM/*nix

1) Python3 and pip must be installed on your PC
2) sudo apt install python3-dev && sudo apt install gcc
3) ```pip3 install -r requirements.txt```
4) Install memcached ```sudo apt install memcached```
5) Edit `config.yaml`:
 - `config_api` you can get from https://ipinfo.io/account/token
 - `token` get from https://t.me/botFather
 - `memcached_ip` - IP of memcached _('localhost' by default)_
 - `memcached_port` - port of memcached _(11211 by default)_
6) Create dir 'files' in project directory
7) run by `python main.py` 

### Self host in docker
1) ```docker pull bitnami/memcached```
2) ```docker network create app-tier --driver bridge``` _(IP of server could be like 172.*.0.2, use nmap btw)_
3) Runing memcached server in background:
```docker run -d --name memcached-server --network app-tier bitnami/memcached:latest```
4) Edit `config.yaml` _(check 5 paragraph in VM/*nix self host)_
5) Build by `docker buildx build .`
6) Run in bg:
```docker run -d --name <docker-name> --network app-tier <container-id>```

### Pull request TO-DO's
- [ ] memcached2dockerfile
- [ ] languages support (ru, eng)
- [ ] https://www.abuseipdb.com
