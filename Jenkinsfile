pipeline {
    agent any

    environment {
        APP_DIR = "/home/cruds/crud_project"
        VENV = "/home/cruds/env"
        PORT = "7282"
        BRANCH = "main"
        BACKUP_DIR = "/home/cruds/backups"
    }

    stages {

        stage('Create Backup') {
            steps {
                sh '''
                    echo "Creating backup..."

                    mkdir -p $BACKUP_DIR

                    # Backup SQLite database
                    if [ -f "$APP_DIR/db.sqlite3" ]; then
                        cp "$APP_DIR/db.sqlite3" \
                        "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3"
                    fi

                    # Backup entire project
                    tar -czf "$BACKUP_DIR/project_$(date +%Y%m%d_%H%M%S).tar.gz" \
                    "$APP_DIR"

                    echo "Backup completed."
                '''
            }
        }

        stage('Sync Latest Code') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        echo "Pulling latest code..."

                        git fetch origin
                        git reset --hard origin/$BRANCH
                        git clean -fd

                        echo "Code synchronized."
                    '''
                }
            }
        }

        stage('Install Requirements') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        source $VENV/bin/activate

                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Makemigrations') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        source $VENV/bin/activate

                        python manage.py makemigrations
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        source $VENV/bin/activate

                        python manage.py migrate
                    '''
                }
            }
        }

        stage('Stop Existing Server') {
            steps {
                sh '''
                    PID=$(lsof -ti:$PORT)

                    if [ ! -z "$PID" ]; then
                        echo "Stopping server..."

                        kill -9 $PID

                        sleep 5
                    else
                        echo "No application running on port $PORT"
                    fi
                '''
            }
        }

        stage('Start Django Server') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        source $VENV/bin/activate

                        mkdir -p server_log

                        nohup python manage.py runserver 0.0.0.0:$PORT \
                        > server_log/django.log 2>&1 &

                        sleep 10
                    '''
                }
            }
        }

        stage('Verify Server') {
            steps {
                sh '''
                    if lsof -i:$PORT > /dev/null
                    then
                        echo "===================================="
                        echo "Application Started Successfully"
                        echo "Running on Port : $PORT"
                        echo "===================================="
                    else
                        echo "===================================="
                        echo "Deployment Failed!"
                        echo "===================================="
                        exit 1
                    fi
                '''
            }
        }

    }

    post {

        success {
            echo 'Deployment Successful'
        }

        failure {
            echo 'Deployment Failed'
        }

        always {
            cleanWs()
        }
    }
}

