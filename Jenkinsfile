#!groovy

//variables from jenkins
properties([disableConcurrentBuilds()])
// agent = env.agent // work agent
// token = env.token // sbercaud token

// pkles-gt0000369
// pkles-gt0003771
// pkles-gt0003772
// pkles-gt0003773


pipeline {
    agent none
//     agent { label 'pkles-gt0000369 || pkles-gt0003771 || pkles-gt0003772 || pkles-gt0003773' }
    options {
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
        timestamps()
        ansiColor('xterm')
    }

    environment {
//         PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
        CMDB_CRED = credentials('cmdb-cred')
        DATA_GERRY_CMDB_URL = "https://cmdb.common.gos-tech.xyz/rest/"
    }
    stages {
        stage('Run Parallel') {
            parallel {

                stage("Update CMDB Info Portal-PD15") {
                    environment {
                        PORTAL_URL_PD15 = 'https://portal.gos.sbercloud.dev'
//                         OS_METRICS_PD15 = 'http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)'
                        OS_METRICS_PD15 = "http://p-infra-internallb.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        PPRB3_VERSIONS_PD15 = 'http://p-infra-jenkinsslave-01.common.novalocal:5002/versions'
                        PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
                    }
                    agent {
                        docker {
//                             label "pkles-gt0003771 || pkles-gt0003772 || pkles-gt0003773"
//                             label "pkles-gt0003771"
//                             label "pkles-gt0003773"
//                             label "pkles-gt0000369 || pkles-gt0003773"
                            label "pkles-gt0000369"
                            registryUrl 'https://base.sw.sbc.space/'
                            image 'pid/pid_registry/datagerry-cmdb/datagerry-cmdb:0.0.1'
                            registryCredentialsId 'tuz_pid_pidefs'
                            args "-u root --privileged --add-host p-infra-bitwarden-01.common.novalocal:172.26.105.1"
                            reuseNode true
                        }
                    }
                    steps {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
//                             sh "./prepare-image-pd15.sh"
                            sh "python3 main.py PD15"
                        }
                    }
                }

                stage("Update CMDB Info Portal-PD20") {
                    environment {
                        PORTAL_URL_PD20 = "https://portal.gostech.novalocal"
                        OS_METRICS_PD20 = "http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        PPRB3_VERSIONS_PD20 = 'http://p-infra-jenkinsslave-01.common.novalocal:5002/versions'
                        PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')

                        FORTI_VPN_HOST = "37.18.109.130:18443"
                        FORTI_VPN_CRED = credentials('fortivpn_cred')
                    }
                    agent {
                        docker {
//                             label "pkles-gt0003772 || pkles-gt0003773 || pkles-gt0000369"
//                             label "pkles-gt0003772"
//                             label "pkles-gt0003773"
//                             label "pkles-gt0000369 || pkles-gt0003773"
//                             image "ubuntu:20.04"
                            label "pkles-gt0000369"
                            registryUrl 'https://base.sw.sbc.space/'
                            image 'pid/pid_registry/datagerry-cmdb/datagerry-cmdb:0.0.1'
                            registryCredentialsId 'tuz_pid_pidefs'
                            args "-u root --privileged --add-host p-infra-bitwarden-01.common.novalocal:172.26.105.1"
                            reuseNode true
                        }
                    }
                    steps {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
//                             sh "sleep 100000"
//                             sh "./prepare-image-fortivpn.sh"
                            sh "screen -dm openfortivpn $FORTI_VPN_HOST -u $FORTI_VPN_CRED_USR -p '$FORTI_VPN_CRED_PSW' --trusted-cert=9b62f7a755070a8bc01cc2f718238d043db90241ce3cdf76621134e85c034bf6"
                            sh "sleep 10"
                            sh "python3 main.py PD20"
//                             sh "ls -la"
                       }
                   }
               }


                stage("Update CMDB Info Portal-PD23") {
                    environment {
                        PORTAL_URL_PD23 = "https://portal.gostech.novalocal"
                        OS_METRICS_PD23 = "http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                        PPRB3_VERSIONS_PD23 = 'http://p-infra-jenkinsslave-01.common.novalocal:5002/versions'
                        PORTAL_TOKEN_PD23 = credentials('PORTAL_TOKEN_PD23')

                        FORTI_VPN_HOST = "193.23.144.132:15443"
                        FORTI_VPN_CRED = credentials('fortivpn_cred_pd23')

                    }
                    agent {
                        docker {
//                             label "pkles-gt0000369 || pkles-gt0003771"
                            label "pkles-gt0003773"
//                             label "pkles-gt0000369"
//                             label "pkles-gt0003772"
//                             label "pkles-gt0003771"
//                             image "ubuntu:20.04"
//                             args "-u root --privileged --add-host p-infra-bitwarden-01.common.novalocal:172.26.105.1 --add-host archive.ubuntu.com:91.189.88.152 --add-host security.ubuntu.com:91.189.88.142"

                            registryUrl 'https://base.sw.sbc.space/'
                            image 'pid/pid_registry/datagerry-cmdb/datagerry-cmdb:0.0.1'
                            registryCredentialsId 'tuz_pid_pidefs'
                            args "-u root --privileged --add-host p-infra-bitwarden-01.common.novalocal:172.26.105.1"
                            reuseNode true
                        }
                    }
                    steps {
//                             sh "./prepare-image-fortivpn.sh"
                            sh "screen -dm openfortivpn $FORTI_VPN_HOST -u $FORTI_VPN_CRED_USR -p '$FORTI_VPN_CRED_PSW' --trusted-cert=3ec488ab55be088c5abb2b137a749d2ef6320c09cefc513d5c02b861a77ee8cd"
                            sh "sleep 10"
                            sh "python3 main.py PD23"
                    }
                }
            }
        }
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




 /*
        stage("Update CMDB Info Portal-PD15") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                DATA_GERRY_CMDB_URL = 'https://cmdb.common.gos-tech.xyz/rest/'
                PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
                PORTAL_URL_PD15 = 'https://portal.gos.sbercloud.dev/api/v1/'
                OS_METRICS_PD15 = 'http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)'
            }

            agent {
                docker {
                    label "pkles-gt0000369"
                    image "base.sw.sbc.space/base/redhat/rhel7:4.5-433"
                    registryUrl "https://base.sw.sbc.space"
                    registryCredentialsId "pidmsk"
                    args "-u root --privileged"
                    reuseNode true
                }
            }
            steps {
                    sh 'bash install-python3.9.sh'
                    sh 'venv/bin/python3.9 main.py'
            }
        }
/*
        stage("Update CMDB Info Portal-PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                DATA_GERRY_CMDB_URL = 'https://cmdb.common.gos-tech.xyz/rest/'
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                PORTAL_URL_PD20 = 'https://portal.gostech.novalocal/api/v1/'
                OS_METRICS_PD20 = 'http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)'
            }

            agent {
                docker {
                    label "pkles-gt0000011-pd20"
                    image "base.sw.sbc.space/base/redhat/rhel7:4.5-433"
                    registryUrl "https://base.sw.sbc.space"
                    registryCredentialsId "pidmsk"
                    args "-u root --privileged"
                    reuseNode true
                }
            }
            steps {
                    sh 'bash install-python3.9.sh'
                    sh 'venv/bin/python3.9 main.py'
            }
        }
*/