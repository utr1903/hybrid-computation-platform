#!/bin/bash

### Set variables
mongodbName="mongodb"
mongodbNamespace="platform"
mongodbRootUserName="root"
mongodbRootPassword="megasecret"
mongodbDatabaseOrganitation="organizations"
mongodbDatabaseOrganitationUsername="organizations"
mongodbDatabaseOrganitationPassword="organizations"

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
  --set auth.rootPassword=${mongodbRootPassword} \
  --set auth.databases[0]=${mongodbDatabaseOrganitation} \
  --set auth.usernames[0]=${mongodbDatabaseOrganitationUsername} \
  --set auth.passwords[0]=${mongodbDatabaseOrganitationPassword} \
  --version "15.6.16" \
  "bitnami/mongodb"
