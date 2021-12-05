#!groovy

//variables from jenkins
properties([disableConcurrentBuilds()])
// agent = env.agent // work agent
// token = env.token // sbercaud token

pipeline {
    agent none
    options {
        buildDiscarder(logRotator(numToKeepStr: '1', artifactNumToKeepStr: '1'))
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
        stage("Update CMDB Info Portal-PD20") {
            environment {
//                 PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
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
                    reuseNode true
                }
            }
            steps {
                    sh 'bash install-python3.9.sh'
                    sh 'python3.9 main.py'
                    sh 'sleep 1000000'
            }
        }

        stage("Update CMDB Info Portal-PD20") {
            environment {
//                 PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
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
                    sh 'python3.9 main.py'
                    sh 'sleep 1000000'

            }
        }
    }
}
    







/*

        stage("PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                FORTI_CRED = credentials('FORTI_CRED')
                def WORKDIR = "${env.WORKSPACE}"
            }

            steps {
                script {
                    echo '''
                    ####################################
                                RUN SCRIPT IN PD20
                    ####################################
                    '''
                    dockerFortiImage = docker.build(fortiImageName, '-f Dockerfile-forticlient ' + env.WORKSPACE)
//                      fortiImageName
//                     sh '''#!/bin/bash
//                     docker build -f Dockerfile-forticlient . -t forti-docker
//                     '''
//                     sh 'docker run --rm --name docker-forticlient --privileged --net host --env-file ${WORKDIR}/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD="${FORTI_CRED_PSW}" forti-docker'
//                     sh 'sleep 1000000'
//                     docker ps -aq -f "name=docker-forticlient"
//                     docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py
//                     sh "docker run -it --rm --name docker-forticlient --privileged --net host --env-file \"${env.WORKSPACE}\"/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD=${FORTI_CRED_PSW} forti-docker"
//                     sh 'docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py'
//                     dockerImage = docker.build imagename
                }
            }
        }


        stage("Build project PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                FORTI_CRED = credentials('FORTI_CRED')
                HOST = "37.18.109.130:18443"
//                 def FORTI_LOGIN = ${FORTI_CRED_USR}
//                 def FORTI_PASS = ${FORTI_CRED_PSW}
            }
            agent {
                docker {
//                     customWorkspace "${env.WORKSPACE}"
//                     Dockerfile 'Dockerfile'
                    image fortiImageName
//                     args "--rm --env-file ${env.WORKSPACE}/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD='${FORTI_CRED_PSW}' forti-docker"
                    args "-u root:sudo --rm --name docker-forticlient --privileged --net host --env-file ${env.WORKSPACE}/.env_PD20"
//                     reuseNode true
//                     label "build-image"
                }
            }
            steps {
//                     sh 'echo "$HOST" $FORTI_CRED_USR $FORTI_CRED_PSW'
//                     sh 'export HOST=${HOST}'
//                     sh 'export FLOGIN=${FORTI_CRED_USR}'
//                     sh 'export FPASS=${FORTI_CRED_PSW}'
//                     sh 'expect /opt/start-connect.exp \'$HOST\' $FORTI_CRED_USR "$FORTI_CRED_PSW"'
//                     sh 'expect /opt/start-connect.exp \"$HOST\" $FORTI_CRED_USR "$FORTI_CRED_PSW"'
//                     sh 'whoami'
//                     sh 'ls -la /opt/start-connect.exp'
//                     sh 'expect /opt/start-connect.exp $HOST $FORTI_CRED_USR $FORTI_CRED_PSW'
//                     sh 'sleep 100000'
                    sh '''python3 main.py'''
//                     sh 'sleep 100000'
//                 }
            }
        }

*/


/*
        stage('Build forti in docker') {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                FORTI_CRED = credentials('FORTI_CRED')
                def WORKDIR = "${env.WORKSPACE}"
            }
            agent {
                dockerfile {
                    dir "${env.WORKSPACE}"
                    filename 'Dockerfile-forticlient'
                    args '--rm --name docker-forticlient --privileged --net host --env-file .env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD=${FORTI_CRED_PSW}'
                }
            }
            steps {
                sh "python3 -V"
                sh 'env'
            }
        }
pipeline{
    agent { dockerfile true }
    stages {
        stage('Test') {
            steps {
                echo "test jenkins pipeline in docker"
            }
        }
    }
}
*/
