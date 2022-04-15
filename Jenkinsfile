#!groovy

properties([disableConcurrentBuilds()])

pipeline {
    agent { label 'pkles-gt0000369 || pkles-gt0003771 || pkles-gt0003772 || pkles-gt0003773' }
    options {
        buildDiscarder(logRotator(numToKeepStr: "30", artifactNumToKeepStr: "30"))
        timestamps()
        ansiColor("xterm")
    }

    environment {
        PYTHONWARNINGS = "ignore:Unverified HTTPS request"
        CMDB_CRED = credentials("cmdb-cred")
        DATA_GERRY_CMDB_URL = "https://cmdb.common.gos-tech.xyz/rest/"
        DG_MONGO_DB_CRED = credentials("DG_MONGO_DB_CRED")
        REGISTRY =  "https://base.sw.sbc.space/"
        IMAGE =  "pid/pid_registry/datagerry-cmdb/datagerry-cmdb:0.0.2"
        REGISTRY_CRED = "tuz_pid_pidefs"
        MONGO_DB =  "p-infra-internallb.common.novalocal:172.26.106.3"
    }
    stages {
//         stage("Run Parallel") {
//             parallel {
                stage("Update CMDB Info Portal-PD15") {
                    environment {
                        PORTAL_URL_PD15 = "https://portal.gos.sbercloud.dev"
                        OS_METRICS_PD15 = "http://p-infra-internallb.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        APP_VERSIONS_PD15 = "http://p-infra-jenkinsslave-01.common.novalocal:5002/PD15versions"
                        PORTAL_TOKEN_PD15 = credentials("PORTAL_TOKEN_PD15")
                    }
                    agent {
                        docker {
//                             label "pkles-gt0000369"
                            registryUrl REGISTRY
                            image IMAGE
                            registryCredentialsId REGISTRY_CRED
                            args "-u root --privileged --add-host $MONGO_DB"
                            reuseNode true
                        }
                    }
                    steps {
                        catchError(buildResult: "SUCCESS", stageResult: "FAILURE") {
                            sh "python3 main.py PD15"
                        }
                    }
                }

                stage("Update CMDB Info Portal-PD20") {
                    environment {
                        PORTAL_URL_PD20 = "https://portal.gostech.novalocal"
                        OS_METRICS_PD20 = "http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        APP_VERSIONS_PD20 = "http://p-infra-jenkinsslave-03.common.novalocal:5002/PD20versions"
                        PORTAL_TOKEN_PD20 = credentials("PORTAL_TOKEN_PD20")
                        FORTI_VPN_HOST = "37.18.109.130:18443"
                        FORTI_VPN_CRED = credentials("fortivpn_cred")
                    }
                    agent {
                        docker {
//                             label "pkles-gt0000369"
                            registryUrl REGISTRY
                            image IMAGE
                            registryCredentialsId REGISTRY_CRED
                            args "-u root --privileged --add-host $MONGO_DB"
                            reuseNode true
                        }
                    }
                    steps {
                        catchError(buildResult: "SUCCESS", stageResult: "FAILURE") {
                            sh "screen -dm openfortivpn $FORTI_VPN_HOST -u $FORTI_VPN_CRED_USR -p '$FORTI_VPN_CRED_PSW' --trusted-cert=9b62f7a755070a8bc01cc2f718238d043db90241ce3cdf76621134e85c034bf6"
                            sh "sleep 10"
                            sh "python3 main.py PD20"
                       }
                   }
               }

                stage("Update CMDB Info Portal-PD23") {
                    environment {
                        PORTAL_URL_PD23 = "https://portal.gostech.novalocal"
                        OS_METRICS_PD23 = "http://p-infra-victoriametrics-01.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        APP_VERSIONS_PD23 = false
                        PORTAL_TOKEN_PD23 = credentials("PORTAL_TOKEN_PD23")
                        FORTI_VPN_HOST = "193.23.144.132:15443"
                        FORTI_VPN_CRED = credentials("fortivpn_cred_pd23")
                    }
                    agent {
                        docker {
//                             label "pkles-gt0003773"
                            registryUrl REGISTRY
                            image IMAGE
                            registryCredentialsId REGISTRY_CRED
                            args "-u root --privileged --add-host $MONGO_DB"
                            reuseNode true
                        }
                    }
                    steps {
                            sh "screen -dm openfortivpn $FORTI_VPN_HOST -u $FORTI_VPN_CRED_USR -p '$FORTI_VPN_CRED_PSW' --trusted-cert=03d57a4c8e580bd17424283763d7e0da8a844715290f789a056906f7f4654260"
                            sh "sleep 10"
                            sh "python3 main.py PD23"
                    }
                }

                stage("Update CMDB Info Portal-PD24") {
                    environment {
                        PORTAL_URL_PD24 = "https://portal.pd24.gtp"
                        OS_METRICS_PD24 = "http://infra-victoriametrics-01.common.pd24.rosim.gtp:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        APP_VERSIONS_PD24 = false
                        PORTAL_TOKEN_PD24 = credentials("PORTAL_TOKEN_PD24")
                        FORTI_VPN_HOST = "178.20.239.116:15443"
                        FORTI_VPN_CRED = credentials("fortivpn_cred_pd24")
                    }
                    agent {
                        docker {
//                             label "pkles-gt0003772"
                            registryUrl REGISTRY
                            image IMAGE
                            registryCredentialsId REGISTRY_CRED
                            args "-u root --privileged --add-host $MONGO_DB"
                            reuseNode true
                        }
                    }
                    steps {
                            sh "screen -dm openfortivpn $FORTI_VPN_HOST -u $FORTI_VPN_CRED_USR -p '$FORTI_VPN_CRED_PSW' --trusted-cert=36fd0c49c63b3bda068fec30c751291cd498376a523c0a1b5f47252fe8798670"
                            sh "sleep 10"
                            sh "python3 main.py PD24"
                    }
                }
//             }
//         }
    }
}

    // }

    // post {
        // always {
            // echo '##############################################################'
            // echo '#################### Clean Work Space ########################'
            // echo '##############################################################'
            // script {
                // echo "clean"
//                 cleanWs notFailBuild: true
//                 cleanWs notFailBuild: false
//                 cleanWs()
//                 echo env.WORKSPACE
            // }
        // }
    // }


//                 withCredentials([usernamePassword(credentialsId: 'fortivpn_cred_pd23', usernameVariable: 'FORTI_USERNAME', passwordVariable: 'FORTI_PASSWORD')]) {
// }