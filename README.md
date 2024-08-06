# hybrid-computation-platform

This repo is dedicated to showcase a commercial hybrid (cloud &amp; on-prem) calculation platform for various workloads.

## Workflow

Get the Kubernetes load balancer IP address:

```shell
CLUSTER_IP_ADDRESS=$(kubectl get svc -n platform ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

Create organization:

```shell
curl -X POST "http://${CLUSTER_IP_ADDRESS}/organizationsgw/create" -d '{"organizationName": "ORGANIZATION_NAME"}'
```

Create job:

```shell
curl -X POST "http://${CLUSTER_IP_ADDRESS}/jobsgw/create" -d '{"organizationId": "ORGANIZATION_ID", "jobName": "JOB_NAME", "timestampRequest": TIMESTAMP_REQUEST}'
```

Update job:

```shell
curl -X POST "http://${CLUSTER_IP_ADDRESS}/jobsgw/update" -d '{"organizationId": "ORGANIZATION_ID", "jobId": "JOB_NAME", "jobStatus": "SUBMITTED"}'
```

List jobs:

```shell
curl -X GET "http://${CLUSTER_IP_ADDRESS}/jobsviz?organizationId=ORGANIZATION_ID"
```

Get job:

```shell
curl -X GET "http://${CLUSTER_IP_ADDRESS}/jobsviz?organizationId=ORGANIZATION_ID&jobId=JOB_ID"
```

Get task to run:

```shell
curl -X GET "http://${CLUSTER_IP_ADDRESS}/tasksgw/task-to-run"
```

Update task:

```shell
curl -X POST "http://${CLUSTER_IP_ADDRESS}/tasksgw/update" -d '{"organizationId": "ORGANIZATION_ID", "taskId": "TASK_ID", "taskStatus": "TASK_STATUS", "timestampUpdated": TIMESTAMP_UPDATED}'
```
