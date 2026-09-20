# Operational notes

- This is a personal TV setup: autologin, passwordless sudo, no screen lock, and VNC without a password or encryption. UFW permits TCP 22/80/443/5900 on IPv4 and IPv6; it does **not** restrict those ports to LAN/Tailscale. Use a trusted network and do not port-forward VNC.
- SSH uses keys, verifies known host keys, validates config before writing, and reloads without ending existing sessions. X11 forwarding retains Debian's enabled setting; TCP and agent forwarding remain disabled.
- The playbook keeps XFCE's native media-key handling and updates sleep settings through the running user session. LightDM changes can restart the desktop; inspect `--check --diff` before applying. There is no automatic reboot or suspend.
- SD automount expects an already-formatted ext4 filesystem labelled `sdcard`. The playbook never formats media. A missing card is allowed.
- Automatic updates match Debian's `trixie-security` origin only, with automatic reboot disabled. Existing unrelated packages are not removed.
- `.env` stays local. SSH uses normal keys/agent/config; set `ANSIBLE_PRIVATE_KEY_FILE` if needed. Keep credentials and machine-specific overrides out of Git.
- Run `--tags validation` after changes; it checks effective SSH policy, APT origin matching, firewall and services. Physical wake/lid behavior still requires checking on the laptop.
