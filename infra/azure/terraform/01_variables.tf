#################
### Variables ###
#################

# Project
variable "project" {
  type = string
}

# Instance
variable "instance" {
  type = string
}

# Datacenter location resources
variable "location" {
  type    = string
  default = "westeurope"
}

# VNET address space
variable "vnet_address_space" {
  type    = string
  default = "192.168.0.0/16"
}

# IP address
variable "ip" {
  type    = string
}
