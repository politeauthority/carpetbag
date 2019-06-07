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
                alwaysPullImage: false
            )
        ],

    volumes: [
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock'),
    ]
) {
    node(label) {
        container("carpetbag") {
            stage('Build Requirements') {
                echo "Running tests/test_carpet_tools.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    pip3 install -r requirements.txt
                    pip3 install -r tests/requirements.txt
                """
            }

            stage('Build CarpetBag') {
                echo "Running tests/test_carpet_tools.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    python3 setup.py build
                    python3 setup.py install
                """
            }

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

            stage('Test Timings') {
                echo "Running tests/test_timings.py"
                checkout scm
                sh """#!/usr/bin/env bash
                    pytest tests/test_timings.py
                """
            }

        }
    }
}
