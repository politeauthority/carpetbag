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
        container("carpetbag") {
            stage('Test CarpetTools') {
                echo "Running tests/test_carpet_tools.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    pytest tests/test_carpet_tools.py
                """
            }

            stage('Test Base') {
                echo "Running tests/test_base_carpetbag.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    pytest tests/test_base_carpetbag.py
                """
            }

            stage('Test Public') {
                echo "Running tests/test_public.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    pytest tests/test_public.py
                """
            }

        }
    }
}
