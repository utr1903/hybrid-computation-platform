#!/bin/bash

### Set variables
kafkaName="kafka"
kafkaNamespace="platform"

###################
### Deploy Helm ###
###################

# Add helm repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# kafka
helm upgrade ${kafkaName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${kafkaNamespace} \
  --set listeners.client.protocol=PLAINTEXT \
  --set provisioning.enabled=true \
  --set provisioning.topics[0].name="createorganization" \
  --set provisioning.topics[0].partitions=3 \
  --set provisioning.topics[1].name="jobrequest" \
  --set provisioning.topics[1].partitions=3 \
  --version "26.6.2" \
  "bitnami/kafka"
