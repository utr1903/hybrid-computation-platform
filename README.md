# hybrid-computation-platform

This repo is dedicated to showcase a commercial hybrid (cloud &amp; on-prem) calculation platform for various workloads.

## Workflow

Create organization:

```shell
kubectl port-forward -n organizations svc/organizationgateway 8080
curl -X POST "http://localhost:8080/create" -d '{"organizationName": "ORGANIZATION_NAME"}'
```

Create job:

```shell
kubectl port-forward -n jobs svc/jobgateway 8080
curl -X POST "http://localhost:8080/create" -d '{"organizationId": "ORGANIZATION_ID", "jobName": "JOB_NAME", "timestampRequest": TIMESTAMP_REQUEST}'
```

Update job:

```shell
kubectl port-forward -n jobs svc/jobgateway 8080
curl -X POST "http://localhost:8080/update" -d '{"organizationId": "ORGANIZATION_ID", "jobId": "JOB_NAME", "jobStatus": "SUBMITTED"}'
```

List jobs:

```shell
kubectl port-forward -n jobs svc/jobvisualizer 8080
curl -X GET "http://localhost:8080/jobs"
```

Get job:

```shell
kubectl port-forward -n jobs svc/jobvisualizer 8080
curl -X GET "http://localhost:8080/jobs/JOB_ID"
```

Get task to run:

```shell
kubectl port-forward -n tasks svc/pipelinevisualizer 8080
curl -X GET "http://localhost:8080/task-to-run"
```

Update task:

```shell
kubectl port-forward -n tasks svc/pipelinegateway 8080
curl -X POST "http://localhost:8080/update" -d '{"organizationId": "ORGANIZATION_ID", "taskId": "TASK_ID", "taskStatus": "TASK_STATUS", "timestampUpdated": TIMESTAMP_UPDATED}'
```
