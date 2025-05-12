#!groovy


pipeline {
    agent any
    stages {
        stage("Build and up") {
            steps {
                sh "echo 1"
                sh "cp ~/workspace/envs/instagramapi-bot.env .env"
                sh "docker compose up -d --build"
            }
        }
    }
}
