//
//

label = "bad-actor-services-web-data-${env.BUILD_NUMBER}"
Image = "politeauthority/carpetbag"

podTemplate(
    label: label,
    name: "jenkins-" + label,
    cloud: "kubernetes",
    containers:
        [
            containerTemplate(
                image: 'docker',
                name: 'docker',
                ttyEnabled: true,
                command: 'cat',
                envVars: [],
                alwaysPullImage: false
            )
        ],
    volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
    ]
) {

    node(label) {
        checkout scm
        container('docker') {
            stage('Build Image') {
                sh """
                    docker build -t carpetbag --no-cache .
                """
            }

            stage('Push Image') {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'Username', passwordVariable: 'Password')]) {
                    sh """
                        docker login -u politeauthority -p $Password
                        docker tag carpetbag ${Image}:latest
                        docker push ${Image}:latest

                        docker tag carpetbag${Image}:${env.BUILD_NUMBER}
                        docker push ${Image}:${env.BUILD_NUMBER}
                    """
                }
            }
        }
    }
}

