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
# databaseAddressMaster="${databaseName}-arbiter-headless.${databaseNamespace}.svc.cluster.local"
databaseAddressMaster="${databaseName}-headless.${databaseNamespace}.svc.cluster.local"
databaseAddressSlave="${databaseName}-headless.${databaseNamespace}.svc.cluster.local"
databaseUsername="customerorg1"
databasePassword="customerorg1"

# cache
cacheName="redis"
cacheNamespace="platform"
cacheAddressMaster="${cacheName}-master.${cacheNamespace}.svc.cluster.local"
cacheAddressSlave="${cacheName}-replicas.${cacheNamespace}.svc.cluster.local"
cachePort=6379
cachePassword="megasecret"

# broker
brokerName="kafka"
brokerNamespace="platform"
brokerAddress="${brokerName}.${brokerNamespace}.svc.cluster.local:9092"

# taskmanager
taskmanagerName="taskmanager"
taskmanagerNamespace="tasks"
taskmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${taskmanagerName}:latest"
taskmanagerReplicas=1

###################
### Deploy Helm ###
###################

# taskmanager
helm upgrade ${taskmanagerName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${taskmanagerNamespace} \
  --set imageName=${taskmanagerImageName} \
  --set imagePullPolicy="Always" \
  --set name=${taskmanagerName} \
  --set replicas=${taskmanagerReplicas} \
  --set database.addresses.master=${databaseAddressMaster} \
  --set database.addresses.slave=${databaseAddressSlave} \
  --set database.username="root" \
  --set database.password="megasecret" \
  --set cache.addresses.master=${cacheAddressMaster} \
  --set cache.addresses.slave=${cacheAddressSlave} \
  --set cache.port=${cachePort} \
  --set cache.password=${cachePassword} \
  --set broker.address=${brokerAddress} \
  "./chart"
