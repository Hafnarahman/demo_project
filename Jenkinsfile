pipeline {
    agent any

    environment {
        APP_DIR = "/home/cruds/crud_project"
        PYTHON = "/home/cruds/env/bin/python"
        PIP = "/home/cruds/env/bin/pip"
        PORT = "7282"
        BRANCH = "main"
        BACKUP_DIR = "/home/cruds/backups"
    }

    stages {

        stage('Create Backup') {
            steps {
                sh '''
                    echo "========== Creating Backup =========="

                    mkdir -p "$BACKUP_DIR"

                    # Backup SQLite DB
                    if [ -f "$APP_DIR/db.sqlite3" ]; then
                        cp "$APP_DIR/db.sqlite3" \
                        "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3"
                    fi

                    # Backup complete project
                    tar -czf "$BACKUP_DIR/project_$(date +%Y%m%d_%H%M%S).tar.gz" \
                    "$APP_DIR"

                    echo "Backup Completed."
                '''
            }
        }

        stage('Sync Latest Code') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Syncing Latest Code =========="

                        git fetch origin
                        git reset --hard origin/$BRANCH

                        # Keep .env while cleaning
                        git clean -fd -e .env

                        echo "Git Sync Completed."
                    '''
                }
            }
        }

        stage('Install Requirements') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Installing Requirements =========="

                        $PIP install --upgrade pip
                        $PIP install -r requirements.txt

                        echo "Requirements Installed."
                    '''
                }
            }
        }

        stage('Makemigrations') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Running Makemigrations =========="

                        $PYTHON manage.py makemigrations
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Running Migrations =========="

                        $PYTHON manage.py migrate
                    '''
                }
            }
        }

        stage('Stop Existing Server') {
            steps {
                sh '''
                    echo "========== Stopping Existing Server =========="

                    PID=$(lsof -ti:$PORT)

                    if [ -n "$PID" ]; then
                        kill -9 "$PID"
                        sleep 5
                        echo "Old Server Stopped."
                    else
                        echo "No server running."
                    fi
                '''
            }
        }

        stage('Start Django Server') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Starting Django Server =========="

                        mkdir -p server_log

                        nohup $PYTHON manage.py runserver 0.0.0.0:$PORT \
                        > server_log/django.log 2>&1 &

                        sleep 10

                        echo "Server Started."
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "========== Verifying Deployment =========="

                    if lsof -i:$PORT >/dev/null
                    then
                        echo "=========================================="
                        echo "Deployment Successful"
                        echo "Application Running on Port $PORT"
                        echo "=========================================="
                    else
                        echo "=========================================="
                        echo "Deployment Failed"
                        echo "=========================================="
                        exit 1
                    fi
                '''
            }
        }
    }

    post {

        success {
            echo "Deployment Successful."
        }

        failure {
            echo "Deployment Failed."
        }

        always {
            cleanWs()
        }
    }
}

