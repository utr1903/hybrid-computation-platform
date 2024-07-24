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
declare -A kafka
kafkaName="kafka"
kafkaNamespace="platform"
kafkaAdress="${kafkaName}.${kafkaNamespace}.svc.cluster.local:9092"
kafkaTopic="jobs"

# gateway
gatewayName="gateway"
gatewayNamespace="jobs"
gatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${gatewayName}:latest"
gatewayReplicas=1

###################
### Deploy Helm ###
###################

# gateway
helm upgrade ${gatewayName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${gatewayNamespace} \
  --set imageName=${gatewayImageName} \
  --set imagePullPolicy="Always" \
  --set name=${gatewayName} \
  --set replicas=${gatewayReplicas} \
  --set kafka.address=${kafkaAdress} \
  --set kafka.topic=${kafkaTopic} \
  "./chart"
