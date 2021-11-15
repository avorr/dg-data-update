#!groovy
//variables from jenkins
properties([disableConcurrentBuilds()])
// agent = env.agent // work agent
// token = env.token // sbercaud token
// stand = env.stand // sbercloud stand
// group = env.group // sbercloud group
// hosts_limit = env.hosts_limit // hosts limit
// keys_repo_url = env.keys_repo_url // url for keys repo
// keys_repo_cred = env.keys_repo_cred // key repository credantials

pipeline {
    agent any
    options {
//         buildDiscarder(logRotator(numToKeepStr: '1', artifactNumToKeepStr: '1'))
        timestamps()
    }

    environment {
        PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
//         withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//         environment {
//             CMDB_LOGIN1 = $USERNAME
//             CMDB_PASSWORD1 = $PASSWORD
//         }
//             sh 'echo $USERNAME'
//             sh 'echo $PASSWORD'
//         }
        imagename = "datagerry-cmdb"
//         registryCredential = 'yenigul-dockerhub'
        dockerImage = ''
        dockerFortiImage = ''
        fortiImageName = 'forti-docker'
    }

//     withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//         environment {
//             CMDB_LOGIN1 = $USERNAME
//             CMDB_PASSWORD1 = $PASSWORD
//         }
//         sh 'echo $USERNAME'
//         sh 'echo $PASSWORD'
//         sh "python3 -V"
//         sh "cat /etc/*-release"
//     }

    stages {
        stage("Prepare build image") {
            steps {
                script {
                    echo '''
                    ####################################
                                BUILD IMAGE
                    ####################################
                    '''
                    dockerImage = docker.build imagename
                    println(env.WORKSPACE)
                }
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



/*
        stage("Build project") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
            }
            agent {
                docker {
//                     customWorkspace "${env.WORKSPACE}"
//                     Dockerfile 'Dockerfile'
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
                    sh '''
                        python3 main.py
                       '''
//                 }
            }
        }
*/
        stage("PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
//                 PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
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
                    args "--rm --env-file ${env.WORKSPACE}/.env_PD20"
//                     reuseNode true
//                     label "build-image"
                }
            }
            steps {
//                 withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                     sh 'echo $USERNAME'
//                     sh 'echo $PASSWORD'
//                     sh 'sleep 100000'
//                     sh 'bash /opt/startvpn.sh'
                    sh '$HOST ${FORTI_CRED_USR} ${FORTI_CRED_PSW}'
                    sh 'expect /opt/start-connect.exp $HOST ${FORTI_CRED_USR} "${FORTI_CRED_PSW}"'
//                     sh '''python3 main.py'''
                    sh 'sleep 100000'
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