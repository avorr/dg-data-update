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
//         /*
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
//                     args "-v ${env.WORKSPACE}:/opt/"
                    reuseNode true
                }
            }
            steps {
//                     sh 'bash install-python3.9.sh'
//                     sh 'venv/bin/python3.9 main.py'
//                     sh 'sleep 10000000'
                    sh "ls -la ${env.WORKSPACE}"
                    echo "${env.WORKSPACE}"

            }
        }
//         */
        /*
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
                    sh 'sleep 1000000000'
                    sh 'bash install-python3.9.sh'
                    sh 'python3.9 main.py'

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
                //чистка workspace
                echo "clean"
//                 cleanWs notFailBuild: true
//                 cleanWs notFailBuild: false
                echo "${env.WORKSPACE}"
            }
        }
    }
}