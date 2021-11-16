#!groovy
//variables from jenkins
properties([disableConcurrentBuilds()])
// agent = env.agent // work agent
// token = env.token // sbercaud token

pipeline {
    agent any
    options {
//         buildDiscarder(logRotator(numToKeepStr: '1', artifactNumToKeepStr: '1'))
        timestamps()
    }

    environment {
        PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
        imagename = "datagerry-cmdb"
//         registryCredential = 'yenigul-dockerhub'
        dockerImage = ''
        dockerFortiImage = ''
        fortiImageName = 'openfortivpn-docker'
    }


    stages {
/*
        stage("Prepare build image for PD15") {
            steps {
                script {
                    echo '''
                    ####################################
                    BUILD IMAGE FOR UPDATE DATAGERRY IN PD15
                    ####################################
                    '''
                    dockerImage = docker.build imagename
                }
            }
        }

        stage("UPDATE DATAGERRY INFO IN PD15") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
            }
            agent {
                docker {
//                     customWorkspace "${env.WORKSPACE}"
                    Dockerfile 'Dockerfile'
                    image "datagerry-cmdb"
                    args "--rm --env-file ${env.WORKSPACE}/.env_PD15"
//                     reuseNode true
//                     label "build-image"
                }
            }
            steps {
//                 withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                     sh 'echo $USERNAME'
//                     sh 'echo $PASSWORD'
                    sh 'python3 main.py'
//                 }
            }
        }

*/


/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




        stage("Prepare build image for PD20") {
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
                    dockerFortiImage = docker.build(fortiImageName, '-f Dockerfile-openfortivpn ' + env.WORKSPACE)
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
//                     args "-u root:sudo --rm --name docker-forticlient --privileged --net host --env-file ${env.WORKSPACE}/.env_PD20"
                    args "--rm --name docker-forticlient --privileged --env-file ${env.WORKSPACE}/.env_PD20"
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

//                     sh '''python3 main.py'''
                    sh 'user=$(id -u)'
                    sh 'group=$(cut -d: -f3 < <(getent group $(whoami)))'
//                     sh 'echo $user'
                    sh 'whoami'
                    sh '''
echo '# ### config file for openfortivpn, see man openfortivpn(1) ###
#
host = 37.18.109.130
port = 18443
username = ${FORTI_CRED_USR}
password = ${FORTI_CRED_PSW}
trusted-cert = 9b62f7a755070a8bc01cc2f718238d043db90241ce3cdf76621134e85c034bf6' > /etc/openfortivpn/config
                    '''
                    sh 'cat /etc/openfortivpn/config'
                    sh 'sleep 10000000000'
//                 }
            }
        }


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
*/



    }
}









/*
        withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
            available as an env variable, but will be masked if you try to print it out any which way
            note: single quotes prevent Groovy interpolation; expansion is by Bourne Shell, which is what you want
            sh 'echo $PASSWORD'
            also available as a Groovy variable
            echo USERNAME
            or inside double quotes for string interpolation
            echo "username is $USERNAME"
        }
*/