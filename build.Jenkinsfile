//
//

label = "carpetbag-build-${env.BUILD_NUMBER}"
// Registry = "politeauthority/tt-scrape"

podTemplate(
    label: label,
    name: "jenkins-" + label,
    cloud: "kubernetes",
    containers:
        [
            containerTemplate(
                image: 'frolvlad/alpine-python3',
                name: 'python3',
                ttyEnabled: true,
                command: 'cat',
                envVars: [],
                alwaysPullImage: true
            )
        ],
    volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
    ]
) {

    node(label) {
        checkout scm
        container('python3') {
            stage('Build Image') {
                sh """
                    docker build -t carpetbag --no-cache .
                """
            }

            stage('Push Image') {
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'Username', passwordVariable: 'Password')]) {
                    sh """
                        docker login -u politeauthority -p $Password
                        docker tag carpetbag politeauthority/carpetbag:latest
                        docker push politeauthority/carpetbag:latest
                    """
                }
            }
        }
    }
}

