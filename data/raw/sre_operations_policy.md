# SRE Operations Policy

## Purpose

This document defines the main operational principles of the SRE team.
The goal of SRE is to maintain reliable, scalable and observable systems
while enabling development teams to deliver changes safely.

## SRE Responsibilities

The SRE team is responsible for:

- Kubernetes platform reliability
- Infrastructure automation
- Monitoring and alerting
- Incident response processes
- Backup and disaster recovery
- Production environment stability

SRE engineers work together with development teams to improve system reliability.

## Task Management Process

All technical requests, incidents and infrastructure changes must be created through the official ticketing system.

Supported request types:

- Incident
- Service request
- Infrastructure change
- Access request
- Security request

Requests created through private messages or informal communication channels should be transferred into the ticketing system.

## Incident Management

Critical incidents must be handled according to severity:

SEV1:
- Production outage
- Immediate response required
- On-call engineer must be involved

SEV2:
- Significant degradation
- Response during working hours

SEV3:
- Minor issues or non-critical problems

Every major incident must have:

- Root cause analysis
- Timeline
- Corrective actions
- Prevention tasks

## Production Changes

Production changes must follow change management principles:

- Changes must be reviewed
- Automated deployment pipelines should be used
- Rollback strategy must exist
- Emergency changes must be documented afterwards

## Communication

SRE engineers communicate through official channels:

- Ticketing system
- Incident channels
- Engineering documentation

Important decisions must be documented and available for future reference.