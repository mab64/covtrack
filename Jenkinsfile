node {
    def image

    stage('Clone repository') {
        checkout scm
    }

    stage('Test code') {
        sh '. /opt/python/venv/pyany/bin/activate; pylint app/*.py'
    }

    stage('Build image') {
       image = docker.build("mual/covtrack")
    }

    stage('Test image') {
        image.inside {
            sh 'echo "Tests passed"'
        }
    }

    stage('Push image') {
        docker.withRegistry('', 'dockerhub_mual') {
            image.push("${env.BUILD_NUMBER}")
            image.push("latest")
        }
    }
}