# Helm

We have the following main operational components to deploy onto the cluster:

- [`ingress-nginx`](/apps/helm/ingress-nginx/)
- [`kafka`](/apps/helm/kafka/)
- [`redis`](/apps/helm/redis/)

In order to deploy them, we can switch to their relevant directories and simply run the `deploy.sh` scripts:

```shell
bash deploy.sh
```
