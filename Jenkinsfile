pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    parameters {
        booleanParam(
            name: 'DEPLOY',
            defaultValue: false,
            description: 'Deploy ke Docker Compose pada agent Jenkins ini (hanya untuk branch main).'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install test dependencies') {
            steps {
                sh 'python3 -m venv .venv && .venv/bin/python -m pip install -r requirements-dev.txt'
            }
        }

        stage('Lint') {
            steps {
                sh '.venv/bin/python -m ruff check app tests migrations tools'
                sh '.venv/bin/python -m compileall -q app tests migrations tools'
            }
        }

        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest -q --junitxml=junit.xml'
            }
            post {
                always {
                    junit testResults: 'junit.xml', allowEmptyResults: true
                }
            }
        }

        stage('Build project report') {
            steps {
                sh '.venv/bin/python tools/build_report.py'
                archiveArtifacts artifacts: 'docs/laporan.pdf', fingerprint: true
            }
        }

        stage('Build container') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy with Docker Compose') {
            when {
                expression { env.BRANCH_NAME == 'main' && params.DEPLOY }
            }
            steps {
                sh 'docker compose up --build -d'
                sh 'docker compose ps'
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}
