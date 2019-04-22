label = "carpetbag-unittest-${UUID.randomUUID().toString()}"
podTemplate(
    label: label,
    cloud: "kubernetes",
    containers:
        [
            containerTemplate(
                image: 'politeauthority/carpetbag:latest',
                name: 'carpetbag',
                ttyEnabled: true,
                command: 'tail -f /dev/null',
                envVars: [],
                alwaysPullImage: true
            )
        ],

    volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
    ]
) {
    node(label) {
        currentBuild.description = "CarpetBag Testing"
        stage('Running unit tests') {
            echo "Running unit tests"
            checkout scm
            container("carpetbag") {
                sh """#!/usr/bin/env bash
                    pytest
                """
            }
        }
    }
}
