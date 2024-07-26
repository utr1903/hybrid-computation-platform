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

# kafka
kafkaName="kafka"
kafkaNamespace="platform"
kafkaAdress="${kafkaName}.${kafkaNamespace}.svc.cluster.local:9092"
kafkaTopic="jobs"

# redis
redisName="redis"
redisNamespace="platform"
redisAdressMaster="${redisName}-master.${redisNamespace}.svc.cluster.local"
redisPort="6379"

# jobcreator
jobcreatorName="jobcreator"
jobcreatorNamespace="jobs"
jobcreatorImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobcreatorName}:latest"
jobcreatorReplicas=1

###################
### Deploy Helm ###
###################

# jobcreator
helm upgrade ${jobcreatorName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${jobcreatorNamespace} \
  --set imageName=${jobcreatorImageName} \
  --set imagePullPolicy="Always" \
  --set name=${jobcreatorName} \
  --set replicas=${jobcreatorReplicas} \
  --set kafka.address=${kafkaAdress} \
  --set kafka.topic=${kafkaTopic} \
  --set redis.addresses.master=${redisAdressMaster} \
  --set redis.port=${redisPort} \
  "./chart"
