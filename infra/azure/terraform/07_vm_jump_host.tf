### Database ###

# Network Security Group for the VM jump host subnet
resource "azurerm_network_security_group" "vm_jh" {
  name                = local.nsg_name_vm_jh
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location
}

# Network Security Rule
resource "azurerm_network_security_rule" "vm_jh_inbound_allow_ssh_to_22" {
  name                        = "AllowSSH"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = local.subnet_cidr_vm_jh
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.platform.name
  network_security_group_name = azurerm_network_security_group.vm_jh.name
}

# Network Security Rule
resource "azurerm_network_security_rule" "vm_jh_inbound_deny_everything" {
  name                        = "DenyAll"
  priority                    = 102
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.platform.name
  network_security_group_name = azurerm_network_security_group.vm_jh.name
}

# Associate NSG with VM jump host subnet
resource "azurerm_subnet_network_security_group_association" "vm_jh" {
  subnet_id                 = azurerm_subnet.vm_jh.id
  network_security_group_id = azurerm_network_security_group.vm_jh.id
}

# Network Interface for the VM
resource "azurerm_network_interface" "vm_jh" {
  name                = local.nic_name_vm_jh
  location            = azurerm_resource_group.platform.location
  resource_group_name = azurerm_resource_group.platform.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.vm_jh.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "vm_jh" {
  name                = local.vm_name_vm_jh
  resource_group_name = azurerm_resource_group.platform.name
  location            = azurerm_resource_group.platform.location

  size           = "Standard_DS1_v2"
  admin_username = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.vm_jh.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  identity {
    type = "SystemAssigned"
  }

  user_data = base64encode(local.init_script_for_vm_jh)
}
