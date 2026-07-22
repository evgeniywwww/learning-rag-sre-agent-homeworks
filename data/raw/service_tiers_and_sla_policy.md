# Service Tiers and SLA Policy

## Purpose

This document defines service classification and reliability expectations for production systems.

## Service Tiers

Services are classified into three tiers.

## Tier 1 - Critical Services

Examples:
- Payment systems
- Authentication services
- Core customer-facing APIs

Requirements:

- 24/7 monitoring
- Defined on-call ownership
- High availability architecture
- Documented disaster recovery procedure

Target SLA:

Availability: 99.9%
Incident response: within 15 minutes

## Tier 2 - Important Services

Examples:
- Internal platforms
- Reporting services
- Supporting APIs

Requirements:

- Business hours monitoring
- Defined support ownership
- Regular backups

Target SLA:

Availability: 99.5%
Incident response: within 1 hour

## Tier 3 - Internal Services

Examples:
- Development tools
- Experimental environments

Requirements:

- Best effort support
- No guaranteed availability

Target SLA:

Availability target: 99%
Incident response: within business hours

## Service Ownership

Every production service must have:

- Technical owner
- Repository
- Documentation
- Monitoring dashboards
- Runbooks