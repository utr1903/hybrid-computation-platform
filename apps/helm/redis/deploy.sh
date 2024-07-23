#!/bin/bash

### Set variables
redisName="redis"
redisNamespace="platform"
redisPassword="megasecret"

###################
### Deploy Helm ###
###################

# Add helm repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# kafka
helm upgrade ${redisName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${redisNamespace} \
  --set auth.password=${redisPassword} \
  --version "18.12.1" \
  "bitnami/redis"
