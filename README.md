# Debian + XFCE on a 2015 MacBook Pro

My Ansible setup for a MacBookPro12,1 (i5, 8 GB) connected to a TV and controlled with an airmouse. Debian 13, XFCE, lid/sleep settings, fan control, SSH and VNC.

This configures an existing Debian installation with the desktop user logged into XFCE. Tailscale is installed separately. Review `inventory.yml` for the hardware and personal defaults.

```sh
# Controller: Python 3.12+ and SSH access to the laptop.
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp .env.example .env
# Edit .env: set TARGET_HOST and PRIMARY_USER.
set -a; . ./.env; set +a
ssh "$ANSIBLE_USER@$TARGET_HOST" true  # verify the host fingerprint first
ansible-playbook site.yml --check --diff --skip-tags validation
ansible-playbook site.yml
```

Read-only checks: `ansible-playbook site.yml --tags validation`.
Local safety checks: `python -m unittest discover -s tests`.

[Operational notes](docs/operations.md) cover the access choices and safe reapplication.
