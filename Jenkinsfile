pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '591424882000'
        AWS_REGION = 'ap-south-1'
        ECR_REPO = 'task-manager-app'
        ECS_CLUSTER = 'task-manager-cluster'
        ECS_SERVICE = 'task-manager-task-service'
        TASK_FAMILY = 'task-manager-task'
        IMAGE_NAME = 'harish5273/task-manager-cicd'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Harish5273/task-manager-cicd.git'
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

        stage('Build & Push to AWS ECR') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
                        // 1. Login to AWS ECR
                        sh 'aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com'
                        
                        // 2. Build the image using the Jenkins BUILD_NUMBER
                        sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
                        
                        // 3. Tag it for AWS ECR
                        sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${BUILD_NUMBER}'
                        
                        // 4. Push to AWS ECR
                        sh 'docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${BUILD_NUMBER}'
                    }
                }
            }
        }

        stage('Deploy to AWS ECS') {
            steps {
                script {
                    withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
                        sh '''
                            # 1. Download the current Task Definition JSON from AWS
                            aws ecs describe-task-definition --task-definition ${TASK_FAMILY} --region ${AWS_REGION} > task-def.json
                            
                            # 2. Use 'sed' to replace the old image tag with the new BUILD_NUMBER in ECR
                            sed -i 's|"image": ".*"|"image": "'${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:${BUILD_NUMBER}'"|g' task-def.json
                            
                            # 3. Register the new Task Definition revision and save the new ARN
                            NEW_TASK_DEF_ARN=$(aws ecs register-task-definition --cli-input-json file://task-def.json --region ${AWS_REGION} --query 'taskDefinition.taskDefinitionArn' --output text)
                            
                            # 4. Update the ECS Service to use this new Task Definition
                            aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --task-definition ${NEW_TASK_DEF_ARN} --region ${AWS_REGION}
                        '''
                    }
                }
            }
        }
    }
}