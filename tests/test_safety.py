"""Offline checks for destructive or access-breaking provisioning regressions."""
from pathlib import Path
import configparser
import unittest

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]


def tasks(role):
    return yaml.safe_load((ROOT / f"ansible/roles/{role}/tasks/main.yml").read_text())


class SafetyTests(unittest.TestCase):
    def test_controller_verifies_host_identity(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(ROOT / "ansible.cfg")
        self.assertTrue(config.getboolean("defaults", "host_key_checking", fallback=True))
        args = config.get("ssh_connection", "ssh_args", fallback="")
        self.assertNotIn("StrictHostKeyChecking=no", args)
        self.assertNotIn("UserKnownHostsFile=/dev/null", args)

    def test_sd_setup_never_formats_media(self):
        for task in tasks("sdcard-automount"):
            self.assertFalse(any(key.endswith(".filesystem") for key in task), task["name"])
            self.assertNotIn("mkfs", str(task))

    def test_ssh_rule_precedes_firewall_activation(self):
        has_allow_rules = False
        for task in tasks("ufw-firewall"):
            ufw = next((value for key, value in task.items() if key.endswith(".ufw")), None)
            if not ufw:
                continue
            if ufw.get("rule") == "allow":
                has_allow_rules = True
            if ufw.get("state") == "enabled":
                self.assertTrue(has_allow_rules, "Enabling UFW before allow rules can lock out SSH")

    def test_ssh_candidate_is_validated_before_install(self):
        config_tasks = [t["ansible.builtin.blockinfile"] for t in tasks("ssh-hardening")
                        if "ansible.builtin.blockinfile" in t]
        self.assertTrue(config_tasks)
        for task in config_tasks:
            self.assertIn("sshd -t -f %s", task.get("validate", ""))

    def test_security_origin_matches_debian_release_metadata(self):
        inventory = yaml.safe_load((ROOT / "inventory.yml").read_text())
        variables = inventory["all"]["children"]["macbook"]["vars"]
        env = Environment(loader=FileSystemLoader(ROOT / "ansible/roles/unattended-upgrades-config/templates"),
                          undefined=StrictUndefined)
        config = env.get_template("50unattended-upgrades.j2").render(**variables)
        self.assertIn("Unattended-Upgrade::Origins-Pattern", config)
        self.assertIn('"origin=Debian,codename=trixie-security,label=Debian-Security";', config)
        self.assertNotIn("Unattended-Upgrade::Allowed-Origins", config)


if __name__ == "__main__":
    unittest.main()
