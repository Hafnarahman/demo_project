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

                    if [ -f "$APP_DIR/db.sqlite3" ]; then
                        cp "$APP_DIR/db.sqlite3" \
                        "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3"
                    fi

                    tar -czf "$BACKUP_DIR/project_$(date +%Y%m%d_%H%M%S).tar.gz" "$APP_DIR"

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

                        # Keep local files
                        git clean -fd \
                            -e .env \
                            -e server_log

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
                    '''
                }
            }
        }

        stage('Makemigrations') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Running Makemigrations =========="

                        $PYTHON manage.py makemigrations --noinput
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "========== Running Migrations =========="

                        $PYTHON manage.py migrate --noinput
                    '''
                }
            }
        }

        stage('Stop Existing Server') {
            steps {
                sh '''
                    echo "========== Stopping Existing Server =========="

                    # Try fuser first
                    fuser -k ${PORT}/tcp 2>/dev/null || true

                    sleep 3

                    # Fallback using ss
                    PID=$(ss -ltnp | grep ":${PORT} " | grep -o 'pid=[0-9]*' | cut -d= -f2 | head -1 || true)

                    if [ -n "$PID" ]; then
                        echo "Killing PID $PID"
                        kill -9 "$PID" || true
                    fi

                    sleep 3
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
                        > server_log/django.log 2>&1 < /dev/null &

                        echo $! > server_log/django.pid

                        sleep 5

                        echo "Started PID:"
                        cat server_log/django.pid
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "========== Verifying Deployment =========="

                    sleep 5

                    if ss -ltn | grep ":${PORT} " >/dev/null; then
                        echo "======================================"
                        echo "Deployment Successful"
                        echo "Running on Port ${PORT}"
                        echo "======================================"
                    else
                        echo "======================================"
                        echo "Deployment Failed"
                        echo "======================================"

                        echo "----- Django Log -----"

                        cat ${APP_DIR}/server_log/django.log || true

                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment Successful"
        }

        failure {
            echo "Deployment Failed"
        }

        always {
            cleanWs()
        }
    }
}