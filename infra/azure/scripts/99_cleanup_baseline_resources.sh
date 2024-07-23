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
    --location)
      location="${2}"
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

# Location
if [[ $location == "" ]]; then
  location="westeurope"
  echo -e "Location [--location] is not provided. Using default location ${location}.\n"
fi

### Set variables
baseResourceGroupName="rg${project}base${instance}"

# Resource group
echo "Checking base resource group [${baseResourceGroupName}]..."
resourceGroup=$(az group show \
  --name $baseResourceGroupName \
  2> /dev/null)

if [[ $resourceGroup == "" ]]; then
  echo -e " -> Resource group does not exist.\n"
else
  echo -e " -> Resource group exists. Deleting..."

  az group delete \
    --name $baseResourceGroupName \
    --yes

  echo -e " -> Resource group is deleted successfully.\n"
fi
