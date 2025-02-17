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
    --platform)
      platform="$2"
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

# Container platform
if [[ $platform == "" ]]; then
  # Default is amd64
  platform="amd64"
else
  if [[ $platform != "amd64" && $platform != "arm64" ]]; then
    echo "Platform [--platform] can either be 'amd64' or 'arm64'."
    exit 1
  fi
fi

### Services ###

# Organizations
organizationgateway="organizationgateway"
organizationmanager="organizationmanager"

# Jobs
jobgateway="jobgateway"
jobmanager="jobmanager"
jobvisualizer="jobvisualizer"

# Tasks
taskgateway="taskgateway"
taskmanager="taskmanager"
taskvisualizer="taskvisualizer"

### Images ###

# Organizations
organizationgatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${organizationgateway}:latest"
organizationmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${organizationmanager}:latest"

# Jobs
jobgatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobgateway}:latest"
jobmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobmanager}:latest"
jobvisualizerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobvisualizer}:latest"

# Tasks
taskgatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${taskgateway}:latest"
taskmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${taskmanager}:latest"
taskvisualizerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${taskvisualizer}:latest"

####################
### Build & Push ###
####################

# organizationgateway
docker build \
  --platform "linux/${platform}" \
  --tag "${organizationgatewayImageName}" \
  --build-arg="APP_NAME=${organizationgateway}" \
  "."
docker push "${organizationgatewayImageName}"

# organizationmanager
docker build \
  --platform "linux/${platform}" \
  --tag "${organizationmanagerImageName}" \
  --build-arg="APP_NAME=${organizationmanager}" \
  "."
docker push "${organizationmanagerImageName}"

# jobgateway
docker build \
  --platform "linux/${platform}" \
  --tag "${jobgatewayImageName}" \
  --build-arg="APP_NAME=${jobgateway}" \
  "."
docker push "${jobgatewayImageName}"

# jobmanager
docker build \
  --platform "linux/${platform}" \
  --tag "${jobmanagerImageName}" \
  --build-arg="APP_NAME=${jobmanager}" \
  "."
docker push "${jobmanagerImageName}"

# jobvisualizer
docker build \
  --platform "linux/${platform}" \
  --tag "${jobvisualizerImageName}" \
  --build-arg="APP_NAME=${jobvisualizer}" \
  "."
docker push "${jobvisualizerImageName}"

# taskgateway
docker build \
  --platform "linux/${platform}" \
  --tag "${taskgatewayImageName}" \
  --build-arg="APP_NAME=${taskgateway}" \
  "."
docker push "${taskgatewayImageName}"

# taskmanager
docker build \
  --platform "linux/${platform}" \
  --tag "${taskmanagerImageName}" \
  --build-arg="APP_NAME=${taskmanager}" \
  "."
docker push "${taskmanagerImageName}"

# taskvisualizer
docker build \
  --platform "linux/${platform}" \
  --tag "${taskvisualizerImageName}" \
  --build-arg="APP_NAME=${taskvisualizer}" \
  "."
docker push "${taskvisualizerImageName}"
