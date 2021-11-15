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






//         withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
            // available as an env variable, but will be masked if you try to print it out any which way
            // note: single quotes prevent Groovy interpolation; expansion is by Bourne Shell, which is what you want
//             sh 'echo $PASSWORD'
            // also available as a Groovy variable
//             echo USERNAME
            // or inside double quotes for string interpolation
//             echo "username is $USERNAME"
//         }





//         stage("Build project") {
//             environment {
//                 CMDB_CRED = credentials('cmdb-cred')
//                 PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
//                 PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
//             }
//             agent {
//                 docker {
////                     customWorkspace "${env.WORKSPACE}"
////                     Dockerfile 'Dockerfile'
//                     image "datagerry-cmdb"
//                     args "--rm --env-file ${env.WORKSPACE}/.env_PD15"
////                     reuseNode true
////                     label "build-image"
//                 }
//             }
//             steps {
////                 withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
////                     sh 'echo $USERNAME'
////                     sh 'echo $PASSWORD'
//                     sh '''
//                         python3 main.py
//                        '''
////                 }
//             }
//         }

        stage("PD20") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
//                 PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
                PORTAL_TOKEN_PD20 = credentials('PORTAL_TOKEN_PD20')
                FORTI_CRED = credentials('FORTI_CRED')
            }

            steps {
                script {
                    echo '''
                    ####################################
                                RUN SCRIPT IN PD20
                    ####################################
                    '''
                    'docker build -f Dockerfile-forticlient . -t forti-docker'
                    sh 'echo ${FORTI_CRED_USR}'
                    sh 'echo ${FORTI_CRED_PSW}'
                    println(env.WORKSPACE)
                    sh 'echo ${env.WORKSPACE}'
                    echo '#########################################'
                    println(env.WORKSPACE)
                    println(env.WORKSPACE)
                    println(buildDir)
                    echo '#########################################'
//                     println(buildDir)

//                     sh "docker run -it --rm --name docker-forticlient --privileged --net host --env-file \"${env.WORKSPACE}\"/.env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD=${FORTI_CRED_PSW} forti-docker"
//                     sh 'docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py'
//                     dockerImage = docker.build imagename
//                     println(env.WORKSPACE)
                }
            }
        }
    }


//     stages {
//         stage('Build') {
//             agent {
//                 dockerfile {
//                     filename 'Dockerfile'
//                     args '-e CMDB_LOGIN=CMDB_LOGIN'
//                 }
//             }
//             steps {
////                 sh "echo ${env}"
//                 sh "python3 env.py"
//                 sh 'env | grep CMD'
////                 sh "cat /etc/*-release"
//             }
//         }
//     }

}