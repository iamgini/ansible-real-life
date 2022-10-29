## Containerfile for custom execution environment
ARG EE_BASE_IMAGE=registry.redhat.io/ansible-automation-platform-22/ee-supported-rhel8:1.0.0-161
ARG EE_BUILDER_IMAGE=registry.redhat.io/ansible-automation-platform-22/ansible-builder-rhel8

FROM $EE_BASE_IMAGE
#USER root
ADD ansible.cfg ansible.cfg
ADD python-packages.tar python
RUN python3 -m pip install -r python/python-packages/requirements.txt --find-links=python/python-packages/ --no-index

# install AWS CLI
RUN microdnf install unzip
# RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o $HOME/awscliv2.zip
# RUN unzip $HOME/awscliv2.zip
# #RUN ./aws/install