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
brokerTopic="jobrequest"

# jobgateway
jobgatewayName="jobgateway"
jobgatewayNamespace="jobs"
jobgatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobgatewayName}:latest"
jobgatewayReplicas=1

###################
### Deploy Helm ###
###################

# jobgateway
helm upgrade ${jobgatewayName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace=${jobgatewayNamespace} \
  --set imageName=${jobgatewayImageName} \
  --set imagePullPolicy="Always" \
  --set name=${jobgatewayName} \
  --set replicas=${jobgatewayReplicas} \
  --set broker.address=${brokerAddress} \
  --set broker.topic=${brokerTopic} \
  "./chart"
