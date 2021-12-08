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
        imagename = "datagerry-cmdb"
//         registryCredential = 'yenigul-dockerhub'
        dockerImage = ''
        dockerFortiImage = ''
        fortiImageName = 'forti-docker'
    }


    stages {
    /*
        stage("Update CMDB Info Portal-PD15") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                TUZ_PID_PIDMSK = credentials('pidmsk')
                DATA_GERRY_CMDB_URL = 'https://cmdb.common.gos-tech.xyz/rest/'
                PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
                PORTAL_URL_PD15 = 'https://portal.gos.sbercloud.dev/api/v1/'
                OS_METRICS_PD15 = 'http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)'
            }

            agent {
                docker {
                    label 'pkles-gt0000369'
                    image 'base.sw.sbc.space/base/redhat/rhel7:4.5-433'
                    registryUrl 'https://base.sw.sbc.space'
                    registryCredentialsId env.TUZ_PID_PIDMSK
                    args "-u root --privileged -v ${env.WORKSPACE}:/opt/"
//                     args "-u root --privileged -v ${env.PWD}/:/opt/"
//                     args "-v ${env.WORKSPACE}:/opt/"
                    reuseNode true
                }
            }
            steps {
                    sh 'bash install-python3.9.sh'
                    sh 'venv/bin/python3.9 main.py'
//                     sh 'sleep 10000000'
//                     sh "ls -la ${env.WORKSPACE}"
//                     sh "ls -la ${env.PWD}"
//                     echo "${env.WORKSPACE}"

            }
        }
        */

        stage("Prepare build image for PD20") {
            agent { label "pkles-gt0000369" }
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                fortivpn_cred = credentials('fortivpn_cred')
                def WORKDIR = "${env.WORKSPACE}"
            }

            steps {
                script {
                    echo '''
                        ####################################
                        Build VPN-Image for Update Cmdb-Info-PD20
                        ####################################
                        '''
//                     dockerFortiImage = docker.build(fortiImageName, '-f Dockerfile-forticlient ' + env.WORKSPACE)
                    dockerFortiImage = docker.build(fortiImageName, '-f Dockerfile-forticlient')
//                      fortiImageName
//                     sh '''#!/bin/bash
//                     docker build -f Dockerfile-forticlient . -t forti-docker
//                     '''
//                     sh 'docker run --rm --name docker-forticlient --privileged --net host --env-file ${WORKDIR}/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${fortivpn_cred_USR} -e PASSWORD="${fortivpn_cred_PSW}" forti-docker'
//                     sh 'sleep 1000000'
//                     docker ps -aq -f "name=docker-forticlient"
//                     docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py
//                     sh "docker run -it --rm --name docker-forticlient --privileged --net host --env-file \"${env.WORKSPACE}\"/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${fortivpn_cred_USR} -e PASSWORD=${fortivpn_cred_PSW} forti-docker"
//                     sh 'docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py'
//                     dockerImage = docker.build imagename
                }
            }
        }



        stage("Update CMDB Info Portal-PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                fortivpn_cred = credentials('fortivpn_cred')
                HOST = "37.18.109.130:18443"
            }
            agent {
                docker {
                    label "pkles-gt0000369"
//                     customWorkspace "${env.WORKSPACE}"
//                     Dockerfile "Dockerfile-forticlient"
                    image fortiImageName
//                     args "--rm --name forticlient --privileged --env-file ${env.WORKSPACE}/.env_PD20 -e HOST=${env.HOST} -e LOGIN=${env.fortivpn_cred_USR} -e PASSWORD=${env.fortivpn_cred_PSW}"
                    args "-u root:sudo --rm --name forticlient --privileged --env-file ${env.WORKSPACE}/.env_PD20"
//                     args "--rm --env-file ${env.WORKSPACE}/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${fortivpn_cred_USR} -e PASSWORD='${fortivpn_cred_PSW}' forti-docker"
//                     args "-u root:sudo --rm --name docker-forticlient --privileged --net host --env-file ${env.WORKSPACE}/.env_PD20"
//                     args "-u 502 --rm --name docker-forticlient --privileged --env-file ${env.WORKSPACE}/.env_PD20"
//                     reuseNode true

                }
            }
            steps {
//                     sh "screen -dm ./start.pl"
//                     sh "/opt/perl-run-fortivpn.pl $HOST $fortivpn_cred_USR '$fortivpn_cred_PSW' &>/tmp/fortilog.txt &"
//                     sh "apt update && apt -y install screen"
//                     sh "screen -dm /opt/perl-run-fortivpn.pl $HOST $fortivpn_cred_USR '$fortivpn_cred_PSW' &>/tmp/fortilog.txt &"
//                     sh '/opt/perl-run-fortivpn.pl $HOST $LOGIN $PASSWORD &>/tmp/fortilog.txt &'
//                     sh "ping p-pprb-iamservice.foms.novalocal"

                    sh "screen -dm /opt/launch-fortivpn.exp $HOST $fortivpn_cred_USR '$fortivpn_cred_PSW'"
                    sh "ping 172.20.18.36"
                    sh "sleep 10000000000"

//                 }
            }
        }

/*
        stage("Update CMDB Info Portal-PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                TUZ_PID_PIDMSK = credentials('pidmsk')
                DATA_GERRY_CMDB_URL = 'https://cmdb.common.gos-tech.xyz/rest/'

                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                PORTAL_URL_PD20 = 'https://portal.gostech.novalocal/api/v1/'
                OS_METRICS_PD20 = 'http://p-infra-nginx-internal.common.novalocal:8481/select/1/prometheus/api/v1/query?query=sum%20(kube_resourcequota)%20by%20(monitor%2C%20namespace%2C%20cluster%2C%20resource%2C%20type)'
            }

            agent {
                docker {
                    label 'pkles-gt0000011-pd20'

                    image 'base.sw.sbc.space/base/redhat/rhel7:4.5-433'
                    registryUrl 'https://base.sw.sbc.space'
                    registryCredentialsId env.TUZ_PID_PIDMSK
                    args "-u root --privileged -v ${env.WORKSPACE}:/opt/"
                    reuseNode true
                }
            }
            steps {
                    sh 'bash install-python3.9.sh'
                    sh 'venv/bin/python3.9 main.py'
            }
        }
*/
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