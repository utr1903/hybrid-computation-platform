### Kubernetes Cluster ###

# Kubernetes Cluster
resource "azurerm_kubernetes_cluster" "platform" {
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
  name                = local.aks_name

  sku_tier = "Standard"

  dns_prefix         = "${local.aks_name}-${azurerm_resource_group.platform.name}"
  kubernetes_version = "1.28.9"

  node_resource_group = local.aks_nodepool_name

  network_profile {
    network_plugin    = "kubenet"
    network_policy    = "calico"
    load_balancer_sku = "standard"
  }

  default_node_pool {
    name    = "system"
    vm_size = "Standard_D2_v2"

    vnet_subnet_id = azurerm_subnet.aks.id

    node_labels = {
      nodePoolName = "system"
    }

    enable_auto_scaling = false
    node_count          = 2

    upgrade_settings {
      drain_timeout_in_minutes      = 0
      max_surge                     = "10%"
      node_soak_duration_in_minutes = 0
    }
  }

  identity {
    type = "SystemAssigned"
  }
}
