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
    --destroy)
      flagDestroy="true"
      shift
      ;;
    --dry-run)
      flagDryRun="true"
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

# Base
baseResourceGroupName="rg${project}base${instance}"
baseStorageAccountName="st${project}base${instance}"
baseBlobContainerName="${project}tfstates"

### Perform Terraform deployment
azureAccount=$(az account show)
tenantId=$(echo $azureAccount | jq -r .tenantId)
subscriptionId=$(echo $azureAccount | jq -r .id)

# Get current IP address
ip=$(curl -s ifconfig.me/ip)

if [[ $flagDestroy != "true" ]]; then

  # Initialize Terraform
  terraform -chdir=../terraform init \
    -upgrade \
    -backend-config="tenant_id=${tenantId}" \
    -backend-config="subscription_id=${subscriptionId}" \
    -backend-config="resource_group_name=${baseResourceGroupName}" \
    -backend-config="storage_account_name=${baseStorageAccountName}" \
    -backend-config="container_name=${baseBlobContainerName}" \
    -backend-config="key=cluster.tfstate"

  # Plan Terraform
  terraform -chdir=../terraform plan \
    -var project=$project \
    -var instance=$instance \
    -var location=$location \
    -var ip=$ip \
    -out "./tfplan"

    if [[ $flagDryRun != "true" ]]; then
    
      # Apply Terraform
      terraform -chdir=../terraform apply tfplan
    fi
else

  # Destroy resources
  terraform -chdir=../terraform destroy \
    -var project=$project \
    -var instance=$instance \
    -var location=$location \
    -var ip=$ip
fi
