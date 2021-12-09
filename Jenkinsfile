#!groovy

//variables from jenkins
properties([disableConcurrentBuilds()])
// agent = env.agent // work agent
// token = env.token // sbercaud token

pipeline {
    agent none
    options {
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
        timestamps()
        ansiColor('xterm')
    }

    environment {
        PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
    }
    stages {

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

        stage("Update CMDB Info Portal-PD20") {
            environment {
                DATA_GERRY_CMDB_URL = "https://cmdb.common.gos-tech.xyz/rest/"
                PORTAL_URL_PD20 = "https://portal.gostech.novalocal/api/v1/"
                OS_METRICS_PD20 = "http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)"
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                FORTI_VPN_HOST = "37.18.109.130:18443"
            }
            agent {
                docker {
                    label "pkles-gt0000369"
                    image "ubuntu:20.04"
                    args "-u root --privileged"
                    reuseNode true
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'fortivpn_cred', usernameVariable: 'FORTI_USERNAME', passwordVariable: 'FORTI_PASSWORD')]) {
                    sh "./prepare-image-pd20.sh"
                    sh "screen -dm ./launch-fortivpn.exp ${FORTI_VPN_HOST} ${FORTI_USERNAME} '${FORTI_PASSWORD}'"
                    sh "python3 main.py"
                }
            }
        }
    }

    post {
        always {
            echo '##############################################################'
            echo '#################### Clean Work Space ########################'
            echo '##############################################################'
            script {
                echo "clean"
//                 cleanWs notFailBuild: true
//                 cleanWs notFailBuild: false
//                 cleanWs()
//                 echo env.WORKSPACE
            }
        }
    }
}