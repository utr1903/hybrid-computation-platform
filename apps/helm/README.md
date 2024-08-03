# Helm

We have the following main operational components to deploy onto the cluster:

- [`ingress-nginx`](/apps/helm/ingress-nginx/)
- [`kafka`](/apps/helm/kafka/)
- [`redis`](/apps/helm/redis/)
- [`jobgateway`](/apps/helm/jobgateway/)
- [`jobmanager`](/apps/helm/jobmanager/)
- [`jobvisualizer`](/apps/helm/jobvisualizer/)

## Platform workloads

These workloads are `ingress-nginx`, `kafka` and `redis`. In order to deploy them, we can switch to their relevant directories and simply run the `deploy.sh` scripts:

```shell
bash deploy.sh
```

## Application workloads

In order to deploy them, we can switch to their relevant directories and simply run the `deploy.sh` scripts:

```shell
bash deploy.sh --project myproj --registry ghcr.io --username myself
```
