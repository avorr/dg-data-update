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
    }

    stages {
        stage('Build') {
            agent {
                dockerfile {
                    filename 'Dockerfile'
//                     tag 'datagerry-cmdb'
                    args '-e CMDB_LOGIN=CMDB_LOGIN'
//                     additionalBuildArgs  '--build-arg version="cmdb-datagerry"'
                }
            }
            steps {
                sh 'docker images'
                sh "docker logs ${c.id}"
                sh "echo ${env.BUILD_ID}"

            }
        }
    }
//     node {
//         git '…'
//         docker.image('datagerry-cmdb').withRun {c ->
//             sh './test-with-local-db'
//         }
//     }
}