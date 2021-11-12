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

// list_of_variables = [agent: agent,
                    //  token : token,
                    //  stand: stand,
                    //  group: group,
                    //  hosts_limit: hosts_limit,
                    //  keys_repo_cred: keys_repo_cred]

pipeline {
    agent any
//     {
//         label agent
//         dockerfile true
//         label any
//         }
    options {
        buildDiscarder(logRotator(numToKeepStr: '1', artifactNumToKeepStr: '1'))
        timestamps()
    }

//     withEnv(['PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin/docker'])
    environment {
//     PATH = "/hot/new/bin:${env.PATH}"
        PATH = "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin"
    }

    stages {
        stage('Build') {
            agent {
                dockerfile {
                    filename 'Dockerfile'
                    label 'datagerry-cmdb'
                }
            }
            steps {
                sh 'ls -la'
            }
        }

//         docker {
//             image 'maven:3.8.1-adoptopenjdk-11'
//             args '-v $HOME/.m2:/root/.m2'
//         }
    }






//     stages {
//         stage('Build the context') {
//             steps {
//                 sh 'docker -h'
//             }
//         }
//     }

        // stage('Run dynamic inventory script') {
        //     steps {
        //         script {
        //             stage('WHOAMI') {
        //                 wrap([$class: 'BuildUser']) {
        //                     def user = env.BUILD_USER_ID
        //                 println(env.WORKSPACE)
        //                 println(env.BUILD_USER)
        //                 }
        //             }
        //             wrap([$class: 'MaskPasswordsBuildWrapper', varPasswordPairs: [[password: token, var: 'PSWD']]]) {
        //                 stage('RUN SCRIPT') {
        //                     catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
        //                         sh 'python3 dynamic_inventory.py ${token} ${stand} ${group}'
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }
        // stage('SCP pub keys repository') {
        //     steps {
        //         dir('keys') {
        //             git branch: 'master',
        //                 credentialsId: keys_repo_cred,
        //                 url: keys_repo_url
        //         }
        //     }
        // }

    //     stage("run ansible-playbook") {
    //         steps {
    //             script {
    //                 if (hosts_limit == null) {
    //                     ansiColor('xterm'){
    //                         ansiblePlaybook(
    //                             playbook: 'playbook.yml',
    //                             inventory: 'inventory.yml',
    //                             colorized: true)
    //                     }
    //                 }

    //                 else {
    //                     ansiColor('xterm'){
    //                         ansiblePlaybook(
    //                             playbook: 'playbook.yml',
    //                             inventory: 'inventory.yml',
    //                             limit: hosts_limit,
    //                             colorized: true)
    //                     }
    //                 }
    //             }
    //         }
    //     }
    // }

    // post {
        // always {
            // sh 'truncate -s0 inventory.yml'
        // }
    // }
}