#!/bin/bash

### Set variables
mongodbName="mongodb"
mongodbNamespace="platform"
mongodbRootUserName="root"
mongodbRootPassword="megasecret"
mongodbUsername1="customerorg1"
mongodbUserPassword1="customerorg1"
mongodbUserDatabase1="customerorg1"

###################
### Deploy Helm ###
###################

# Add helm repos
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# kafka
helm upgrade ${mongodbName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${mongodbNamespace} \
  --set architecture="replicaset" \
  --set replicaCount=2 \
  --set auth.enabled=true \
  --set auth.rootUser=${mongodbRootUserName} \
  --set auth.password=${mongodbRootPassword} \
  --set auth.usernames[0]=${mongodbUsername1} \
  --set auth.passwords[0]=${mongodbUserPassword1} \
  --set auth.databases[0]=${mongodbUserDatabase1} \
  --version "15.6.16" \
  "bitnami/mongodb"
