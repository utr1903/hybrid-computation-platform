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

# redis
redisName="redis"
redisNamespace="platform"
redisAdressMaster="${redisName}-master.${redisNamespace}.svc.cluster.local"
redisAdressSlaves="${redisName}-replicas.${redisNamespace}.svc.cluster.local"
redisPort="6379"

# jobmanager
jobmanagerName="jobmanager"
jobmanagerNamespace="jobs"
jobmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobmanagerName}:latest"
jobmanagerReplicas=1

###################
### Deploy Helm ###
###################

# jobmanager
helm upgrade ${jobmanagerName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${jobmanagerNamespace} \
  --set imageName=${jobmanagerImageName} \
  --set imagePullPolicy="Always" \
  --set name=${jobmanagerName} \
  --set replicas=${jobmanagerReplicas} \
  --set redis.addresses.master=${redisAdressMaster} \
  --set redis.addresses.slaves=${redisAdressSlaves} \
  --set redis.port=${redisPort} \
  "./chart"
