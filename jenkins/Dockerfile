FROM jenkins/jenkins:lts-jdk21

USER root

# The official Jenkins image intentionally omits Python and the Docker CLI.
# Debian 13 provides Python 3.13, compatible with this project's Python 3.12+ code.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl python3 python3-venv python3-pip \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian trixie stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN jenkins-plugin-cli --plugins \
    "workflow-aggregator github github-branch-source pipeline-stage-view junit"

COPY jenkins/init.groovy.d /usr/share/jenkins/ref/init.groovy.d

USER jenkins
