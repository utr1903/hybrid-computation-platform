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

# broker
brokerName="kafka"
brokerNamespace="platform"
brokerAddress="${brokerName}.${brokerNamespace}.svc.cluster.local:9092"

# taskgateway
taskgatewayName="taskgateway"
taskgatewayNamespace="tasks"
taskgatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${taskgatewayName}:latest"
taskgatewayReplicas=1

###################
### Deploy Helm ###
###################

# taskgateway
helm upgrade ${taskgatewayName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${taskgatewayNamespace} \
  --set imageName=${taskgatewayImageName} \
  --set imagePullPolicy="Always" \
  --set name=${taskgatewayName} \
  --set replicas=${taskgatewayReplicas} \
  --set broker.address=${brokerAddress} \
  "./chart"
