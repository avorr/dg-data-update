# How to

## Requirements
#### docker

## Required environment variables

CMDB_LOGIN - DATA GERRY ("https://cmdb.common.gos-tech.xyz/") Login, "portal_monitoring" by default<br>
CMDB_PASSWORD - Your Bitwarden Password<br>
PORTAL_TOKEN_PD15 - Token from portal pd15 ("https://portal.gos.sbercloud.dev/client/settings?section=tokens") <br>

```bash
export CMDB_LOGIN='portal_monitoring'
export CMDB_PASSWORD='Password'
export PORTAL_TOKEN_PD15='TOKEN'
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