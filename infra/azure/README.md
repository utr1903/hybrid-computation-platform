# Azure

## 01 - Setting up baseline

For provisioning Azure Kubernetes Service (AKS), we will be using Terraform which needs to store the state of the deployment somewhere. That storage is a blob container within a storage account which is supposed to be available in advance to the AKS provisioning.

This pre-setup is called the baseline and can be created with the script [`00_create_baseline_resources.sh`](/infra/azure/scripts/00_create_baseline_resources.sh). It is important to note that this script should be run by a user (or a sevice principal) who has `Owner` rights on the subscription level!

```shell
bash 00_create_baseline_resources.sh --project myproj --instance 001 --location westeurope
```

The following Azure resources will be deployed:

1. Resource group [`rg${project}base${instance}`] (to group all baseline resources)
2. Storage account [`st${project}base${instance}`] (for Terraform blob container)
3. Blob container [`${project}tfstates`] (to store Terraform state)

## 02 - Provisioning platform setup

After the baseline components are created, the cluster and it's relevant resources can be provisioned. In order to do that, run the script [`01_deploy_setup.sh`](/infra/azure/scripts/01_deploy_setup.sh).

```shell
bash 01_deploy_setup.sh --project myproj --instance 001 --location westeurope
```

**IMPORTANT**: The `project`, `instance` and `location` should be the same as the ones in the baseline!

The following Azure resources will be deployed:

1. Resource group [`rg${project}platform${instance}`] (to group all platform resources)
2. AKS [`aks${project}platform${instance}`] (cluster itself)
3. AKS resource group [`rgaks${project}platform${instance}`] (to group the cluster nodepools)

## 03 - Getting AKS credentials

After the AKS is created, we are ready to deploy our workloads! In order to contact the cluster, we requiret it's credentials.

```shell
bash 02_get_aks_credentials.sh --project myproj --instance 001
```

## 04 - Cleaning up

After we are done with the entire environment, we need to clean up everything we have created. In order to that, do the following sequentially:

First, we destroy the Terraform deployment:

```shell
bash 01_deploy_setup.sh --project myproj --instance 001 --location westeurope --destroy
```

Next, we delete the baseline resources by running the clean up script [`99_cleanup_baseline_resources.sh`](/infra/azure/scripts/99_cleanup_baseline_resources.sh).

```shell
bash 99_cleanup_baseline_resources.sh --project myproj --instance 001 --location westeurope --destroy
```

**IMPORTANT**: The `project`, `instance` and `location` should be the same as the ones in the baseline and platform!
