pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Harish5273/task-manager-cicd.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t harish5273/task-manager-cicd:${BUILD_NUMBER} .'
                sh 'docker tag harish5273/task-manager-cicd:${BUILD_NUMBER} harish5273/task-manager-cicd:latest'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
                        docker push harish5273/task-manager-cicd:${BUILD_NUMBER}
                        docker push harish5273/task-manager-cicd:latest
                        docker logout
                    '''
                }
            }
        }
    }
}    