#!groovy

properties([disableConcurrentBuilds()])

pipeline {
    agent { label 'pkles-gt0012105-pd15 || pkles-gt0012100-pd15 || pkles-gt0012102-pd15 || pkles-gt0012098-pd15 || pkles-gt0012099-pd15' }
    options {
        buildDiscarder(logRotator(numToKeepStr: "30", artifactNumToKeepStr: "30"))
        timestamps()
        ansiColor("xterm")
    }
    triggers {
        cron('0 */4 * * *')
    }
    environment {
        PYTHONWARNINGS = "ignore:Unverified HTTPS request"
        DG = credentials("DG")
        DG_URL = "https://cmdb.gos-tech.xyz/rest/"
        DG_MONGODB = credentials("DG_MONGODB")
        DG_MONGODB_HOST = "p-infra-internallb.common.novalocal:27017/cmdb"
        REGISTRY =  "https://base.sw.sbc.space/"
        IMAGE =  "pid/pid_registry/datagerry-cmdb/datagerry-cmdb:0.0.3"
        REGISTRY_CRED = "tuz_pid_pidefs"
        MONGO_DB =  "p-infra-internallb.common.novalocal:172.26.106.3"
    }
    stages {
        stage("Update CMDB Info Portal-PD15") {
            environment {
                PORTAL_URL = "https://portal.gos.sbercloud.dev"
                K8S_METRICS = "http://vm_select.pd15.admin.gtp:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                APP_VERSIONS = "http://infra-jenkinsslave-04.pd15.admin.gtp:5002/versions-pd15"
                PORTAL_TOKEN = credentials("PORTAL_TOKEN")
            }
            agent {
                docker {
                    registryUrl REGISTRY
                    image IMAGE
                    registryCredentialsId REGISTRY_CRED
                    args "-u root --privileged --add-host $MONGO_DB"
                    reuseNode true
                }
            }
            steps {
                catchError(buildResult: "SUCCESS", stageResult: "FAILURE") {
                    sh "./main.py PD15"
                }
            }
        }
/*
        stage("Update visible settings") {
            agent {
                docker {
                    registryUrl REGISTRY
                    image IMAGE
                    registryCredentialsId REGISTRY_CRED
                    args "-u root --privileged --add-host $MONGO_DB"
                    reuseNode true
                }
            }
            steps {
                    sh "./view_settings.py"
            }
        }
*/
    }
}