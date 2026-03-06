# 37-aws-reliability-security-redis

A portfolio-grade **Redis reliability and security** toolkit:
offline demos, deterministic guardrails, and explicit validation modes.

## The top pains this repo addresses
1) Making stateful services boring again—predictable performance, safe backups, and repeatable recovery drills.
2) Replacing manual, risky changes with automation—repeatable infrastructure and safer operational workflows.
3) Enforcing security and governance without slowing delivery—explicit guardrails and production-safe validation paths.

## Quick demo (local)
Prereqs: Docker + Docker Compose (for the container lab).

```bash
make up
make seed
make check
make backup
make restore
```

What you get:
- a Redis primary + replica lab (password-protected)
- a safe replication check drill
- a deterministic backup/restore drill for demo keys (`demo:*`)

## Tests (two explicit modes)

- `TEST_MODE=demo` (default): offline-only checks, deterministic artifacts
- `TEST_MODE=production`: real integrations (requires explicit opt-in + configuration)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

Production integration options:
- Set `REDIS_TEST_URL` (or `REDIS_TEST_HOST`/`REDIS_TEST_PORT`) to run a real Redis `PING` check
- Optionally set `TERRAFORM_VALIDATE=1` to validate the included Terraform example (requires `terraform`)

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
