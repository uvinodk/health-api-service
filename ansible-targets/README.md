# Ansible Test Target

This directory contains a Docker-based test environment for Ansible playbooks.

## Setup

1. Build and start the test target:
   ```bash
   cd ansible-targets
   docker-compose up -d
   ```

2. Verify the container is running:
   ```bash
   docker ps | grep ansible-test-target
   ```

3. Test SSH connection:
   ```bash
   ssh ansible@localhost -p 2222
   # Password: ansible
   ```

## Running Ansible Playbooks

From the `ansible-infra` directory:

```bash
cd ../ansible-infra
ansible-playbook playbooks/dev.yml
```

## Cleanup

```bash
cd ansible-targets
docker-compose down
```
