#!/bin/bash

# Get commandline arguments
while (( "$#" )); do
  case "$1" in
    --project)
      project="${2}"
      shift
      ;;
    --registry)
      containerRegistry="${2}"
      shift
      ;;
    --username)
      containerRegistryUsername="${2}"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Project
if [[ $project == "" ]]; then
  echo -e "Project [--project] is not provided!\n"
  exit 1
fi

# Container registery
if [[ $containerRegistry == "" ]]; then
  echo "Container registery [--registry] is not provided! Using default [ghcr.io]..."
  containerRegistry="ghcr.io"
fi

# Container registery username
if [[ $containerRegistryUsername == "" ]]; then
  echo "Container registery username [--username] is not provided! Using default [utr1903]..."
  containerRegistryUsername="utr1903"
fi

### Set variables

# database
databaseName="mongodb"
databaseNamespace="platform"
databaseAddressMaster="${databaseName}-headless.${databaseNamespace}.svc.cluster.local"
databaseAddressSlave="${databaseName}-headless.${databaseNamespace}.svc.cluster.local"
databaseUsername="root"
databasePassword="megasecret"

# broker
brokerName="kafka"
brokerNamespace="platform"
brokerAddress="${brokerName}.${brokerNamespace}.svc.cluster.local:9092"
brokerConsumerGroup="organizationmanager"

# organizationmanager
organizationmanagerName="organizationmanager"
organizationmanagerNamespace="organizations"
organizationmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${organizationmanagerName}:latest"
organizationmanagerReplicas=1

###################
### Deploy Helm ###
###################

# organizationmanager
helm upgrade ${organizationmanagerName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${organizationmanagerNamespace} \
  --set imageName=${organizationmanagerImageName} \
  --set imagePullPolicy="Always" \
  --set name=${organizationmanagerName} \
  --set replicas=${organizationmanagerReplicas} \
  --set database.addresses.master=${databaseAddressMaster} \
  --set database.addresses.slave=${databaseAddressSlave} \
  --set database.username=${databaseUsername} \
  --set database.password=${databasePassword} \
  --set broker.address=${brokerAddress} \
  --set broker.consumerGroup=${brokerConsumerGroup} \
  "./chart"
