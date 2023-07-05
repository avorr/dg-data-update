# How to

## Requirements
#### docker

## Required environment variables

DG_USR - DATA GERRY ("https://cmdb.common.gos-tech.xyz/") Login, "portal_monitoring" by default<br>
DG_PSW - Your Bitwarden Password<br>
PORTAL_TOKEN - Token from portal pd15 ("https://portal.gos.sbercloud.dev/client/settings?section=tokens") <br>

```bash
export APP_VERSIONS=""
export DG_MONGODB_HOST=""
export DG_MONGODB_PSW=""
export DG_MONGODB_USR=""
export DG_PSW=""
export DG_URL=""
export DG_USR=""
export K8S_METRICS=""
export PASSPORTS_URL=""
export PORTAL_TOKEN=""
export PORTAL_URL=""
export REGION=""

```

### Usage example

**Container build**
```bash
docker build -t datagerry-cmdb .   
```

**Start** 
```bash
docker run --env-file .env -e PORTAL_TOKEN_PD15=$PORTAL_TOKEN_PD15 -e CMDB_LOGIN=$CMDB_LOGIN -e CMDB_PASSWORD=$CMDB_PASSWORD --rm -it datagerry-cmdb
```