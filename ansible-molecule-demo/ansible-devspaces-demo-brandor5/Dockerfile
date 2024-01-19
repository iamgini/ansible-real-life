# quay.io/ansible/creator-ee:v0.21.0
FROM quay.io/ansible/creator-ee@sha256:bf95ae745601a9d199eeb12807be24413fc2d6488016069816ee74342c2c255b

ENV HOME=/home/runner

# install additional modules required by ansible
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

## kubectl
RUN \
    microdnf install -y which && \
    microdnf clean all && \
    curl -LO https://dl.k8s.io/release/`curl -LS https://dl.k8s.io/release/stable.txt`/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin && \
    kubectl version --client

## helm
RUN \
    TEMP_DIR="$(mktemp -d)" && \
    cd "${TEMP_DIR}" && \
    HELM_VERSION="3.7.0" && \
    HELM_ARCH="linux-amd64" && \
    HELM_TGZ="helm-v${HELM_VERSION}-${HELM_ARCH}.tar.gz" && \
    HELM_TGZ_URL="https://get.helm.sh/${HELM_TGZ}" && \
    curl -sSLO "${HELM_TGZ_URL}" && \
    curl -sSLO "${HELM_TGZ_URL}.sha256sum" && \
    sha256sum -c "${HELM_TGZ}.sha256sum" 2>&1 | grep OK && \
    tar -zxvf "${HELM_TGZ}" && \
    mv "${HELM_ARCH}"/helm /usr/local/bin/helm && \
    cd - && \
    rm -rf "${TEMP_DIR}"

# nodejs 18 + VSCODE_NODEJS_RUNTIME_DIR are required on ubi9 based images
# until we fix https://github.com/eclipse/che/issues/21778
# When fixed, we won't need this Dockerfile anymore.
# c.f. https://github.com/che-incubator/che-code/pull/120
RUN \
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash && \
export NVM_DIR="$HOME/.nvm" && \
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
nvm install 18.18.0
ENV VSCODE_NODEJS_RUNTIME_DIR="$HOME/.nvm/versions/node/v18.18.0/bin/"

# Set permissions on /etc/passwd and /home to allow arbitrary users to write
RUN chgrp -R 0 /home && chmod -R g=u /etc/passwd /etc/group /home
