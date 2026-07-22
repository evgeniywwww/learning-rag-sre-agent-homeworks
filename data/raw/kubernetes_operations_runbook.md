# Kubernetes Operations Runbook

## Pod Restart Investigation

When a Kubernetes pod restarts repeatedly, engineers should check:

## Step 1: Pod Status

Check:

- Pod events
- Restart count
- Container status

## Step 2: Application Logs

Review:

- Application errors
- Stack traces
- Connection failures

## Step 3: Resource Usage

Check:

- CPU consumption
- Memory usage
- OOMKilled events

## Step 4: Recent Changes

Review:

- Latest deployments
- Configuration changes
- Environment variables

## Possible Actions

Depending on the root cause:

- Rollback deployment
- Increase resources
- Fix configuration
- Restart unhealthy components

All production changes must be documented.