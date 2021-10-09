def image
pipeline {
	agent any
	stages {
		stage('Test code') {
			steps {
				sh '. /opt/python/venv/pyany/bin/activate; pylint -E app/*.py'
			}
		}

		stage('Build image') {
			steps {
				script {
					image = docker.build("mual/covtrack")
				}
			}
		}

		// // stage('Test image') {
		// //     image.inside {
		// //         sh 'echo "Tests passed"'
		// //     }
		// // }

		stage('Push image') {
			steps {
				script {
					docker.withRegistry('', 'dockerhub_mual') {
						image.push("${env.BUILD_NUMBER}")
						image.push("latest")
					}
				}
			}
		}

		stage('Run container locally') {
			environment {
				CNT_NAME = "covtrack"
				ENV_FILE = credentials('covtrack_env')
				MYSQL_PASSWD = credentials('covtrack_mysql_passwd')
			}
			steps {
				sh 'docker rm -f ${CNT_NAME}; \
				docker run -dit -p 5001:5000 \
				--env-file ${ENV_FILE} \
				--restart on-failure:3 --name ${CNT_NAME} \
				mual/${CNT_NAME}:${BUILD_NUMBER}'
			}
		}
	}
}

	// :${BUILD_NUMBER}
					// -e MYSQL_HOST=192.168.88.10 \
					// -e MYSQL_DATABASE=covtrack \
					// -e MYSQL_USER=covtrack \
					// -e MYSQL_PASSWORD="CovidTracker_2021"\