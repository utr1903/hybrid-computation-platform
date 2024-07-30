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

# Services
gateway="gateway"
jobmanager="jobmanager"
jobvisualizer="jobvisualizer"

# Images
gatewayImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${gateway}:latest"
jobmanagerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobmanager}:latest"
jobvisualizerImageName="${containerRegistry}/${containerRegistryUsername}/${project}-${jobvisualizer}:latest"

####################
### Build & Push ###
####################

# gateway
docker build \
  --platform "linux/${platform}" \
  --tag "${gatewayImageName}" \
  --build-arg="APP_NAME=${gateway}" \
  "./${gateway}"
docker push "${gatewayImageName}"

# jobmanager
docker build \
  --platform "linux/${platform}" \
  --tag "${jobmanagerImageName}" \
  --build-arg="APP_NAME=${jobmanager}" \
  "./${jobmanager}"
docker push "${jobmanagerImageName}"

# jobvisualizer
docker build \
  --platform "linux/${platform}" \
  --tag "${jobvisualizerImageName}" \
  --build-arg="APP_NAME=${jobvisualizer}" \
  "./${jobvisualizer}"
docker push "${jobvisualizerImageName}"