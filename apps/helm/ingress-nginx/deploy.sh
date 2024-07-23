#!/bin/bash

### Set variables
ingressNginxName="ingress-nginx"
ingressNginxNamespace="platform"

###################
### Deploy Helm ###
###################

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# ingress-nginx
helm upgrade ${ingressNginxName} \
  --install \
  --wait \
  --debug \
  --create-namespace \
  --namespace ${ingressNginxNamespace} \
  --set controller.admissionWebhooks.patch.nodeSelector."kubernetes\.io/os"=linux \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --set controller.service.externalTrafficPolicy=Local \
  ingress-nginx/ingress-nginx
