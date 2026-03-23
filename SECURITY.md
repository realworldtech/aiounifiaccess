# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly via [GitHub Security Advisories](https://github.com/rwts/aiounifiaccess/security/advisories/new).

**Please do not open a public issue for security vulnerabilities.**

We will acknowledge receipt within 48 hours and aim to release a fix within
7 days for critical issues.

## Scope

This library is a client for the UniFi Access API. Security issues in scope include:

- Credential or token leakage
- Improper TLS/certificate handling
- Webhook signature verification bypasses
- Injection vulnerabilities in API request construction
