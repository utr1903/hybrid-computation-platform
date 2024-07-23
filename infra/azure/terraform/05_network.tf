### Network ###

# VNET
resource "azurerm_virtual_network" "platform" {
  name                = local.vnet_name
  address_space       = [var.vnet_address_space]
  location            = azurerm_resource_group.platform.location
  resource_group_name = azurerm_resource_group.platform.name
}

# Subnet - AKS
resource "azurerm_subnet" "aks" {
  name                 = "aks"
  resource_group_name  = azurerm_resource_group.platform.name
  virtual_network_name = azurerm_virtual_network.platform.name
  address_prefixes = [
    local.subnet_cidr_aks,
  ]
}

# Subnet - VM jump host
resource "azurerm_subnet" "vm_jh" {
  name                 = "vm_jump_host"
  resource_group_name  = azurerm_resource_group.platform.name
  virtual_network_name = azurerm_virtual_network.platform.name
  address_prefixes = [
    local.subnet_cidr_vm_jh,
  ]
}
