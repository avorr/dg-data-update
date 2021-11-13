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
//         PORTAL_TOKEN_PD15 = "TEST"


//         withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//         environment {
//             CMDB_LOGIN1 = $USERNAME
//             CMDB_PASSWORD1 = $PASSWORD
//         }
//             sh 'echo $USERNAME'
//             sh 'echo $PASSWORD'
//             sh "python3 -V"
//             sh "cat /etc/*-release"
//         }

//         CMDB_LOGIN = credantials('cmdb-cred')
//         CMDB_LOGIN = 'TEST'
//         CMDB_PASSWORD = "TEST"
        imagename = "datagerry-test"
//         registryCredential = 'yenigul-dockerhub'
        dockerImage = ''

    }

//     withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//         environment {
//
//             CMDB_LOGIN1 = $USERNAME
//             CMDB_PASSWORD1 = $PASSWORD
//
//
//         }
//         sh 'echo $USERNAME'
//         sh 'echo $PASSWORD'
//         sh "python3 -V"
//         sh "cat /etc/*-release"
//     }



    stages {
        stage("Prepare build image") {
//             environment {
//                 test = TESTTT
//                 test2 = ''
//             }

        steps {

//             withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                 test = $USERNAME
//                 test2 = $PASSWORD
//             }

                sh 'echo prinvet'
            }
        }

        stage("build image") {
            steps {
                script {
                    dockerImage = docker.build imagename
                    sh 'ls -la'
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

        stage("Build project") {
            environment {
                CMDB_CRED = credentials('cmdb-cred')
                PORTAL_TOKEN_PD15 = credentials('PORTAL_TOKEN_PD15')
//                 CMDB_PASSWORD1 = $PASSWORD
            }
            agent {
                docker {

//                     Dockerfile 'Dockerfile'
                    image "datagerry-test"
                    args "--env-file $HOME/.env"
                    reuseNode true
//                     label "build-image"
                }
            }
            steps {
//                 withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                     sh 'echo $USERNAME'
//                     sh 'echo $PASSWORD'
//                     sh "python3 -V"
//                     sh "cat /etc/*-release"
//                     println(CMDB_CRED)
                    sh '''
                        env
                        python3 main.py
                       '''
//                 }



//                 sh "echo ##################################################"
//                     withCredentials([usernamePassword(credentialsId: 'cmdb-cred', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                      sh '''
//                         echo "$USERNAME"
//                         echo "$PASSWORD"
//                         '''
//                     }

//                 echo CMDB_LOGIN
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