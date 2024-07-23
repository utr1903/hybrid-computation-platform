##############
### Locals ###
##############

locals {

  # Resource group
  resource_group_name = "rg${var.project}platform${var.instance}"

  # Virtual network
  vnet_name     = "vnet${var.project}platform${var.instance}"
  priv_dns_name = "prvdns${var.project}platform${var.instance}"

  # AKS
  subnet_cidr_aks   = cidrsubnet(var.vnet_address_space, 4, 1)
  aks_name          = "aks${var.project}platform${var.instance}"
  aks_nodepool_name = "aks${var.project}npplatform${var.instance}"

  # VM - jump host
  subnet_cidr_vm_jh = cidrsubnet(var.vnet_address_space, 4, 2)
  nsg_name_vm_jh    = "nsg${var.project}platform${var.instance}jh"
  pubib_name_vm_jh  = "pubip${var.project}platform${var.instance}jh"
  nic_name_vm_jh    = "nic${var.project}platform${var.instance}jh"
  vm_name_vm_jh     = "vm${var.project}platform${var.instance}jh"
  # User data
  init_script_for_vm_jh = <<SCRIPT
#!/bin/bash

#############################
### TESTING PURPOSES ONLY ###
#############################

sudo mkdir /tmp/test

#############################
#############################

# Update & upgrade
sudo apt-get update
echo "Y" | sudo apt-get upgrade

SCRIPT
}
