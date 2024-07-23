#!/bin/bash

# Get commandline arguments
while (( "$#" )); do
  case "$1" in
    --project)
      project="${2}"
      shift
      ;;
    --instance)
      instance="${2}"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

### Check input

# Project
if [[ $project == "" ]]; then
  echo -e "Project [--project] is not provided!\n"
  exit 1
fi

# Instance
if [[ $instance == "" ]]; then
  echo -e "Instance [--instance] is not provided!\n"
  exit 1
fi

# Set variables
mainResourceGroupName="rg${project}platform${instance}"
mainAksResourceName="aks${project}platform${instance}"

# Get AKS credentials
az aks get-credentials \
  --resource-group $mainResourceGroupName \
  --name $mainAksResourceName \
  --overwrite-existing
