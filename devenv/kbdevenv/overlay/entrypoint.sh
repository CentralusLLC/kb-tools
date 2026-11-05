#!/bin/sh
# Generate a stable host key (kept in a volume across rebuilds), prepare the
# agent's home and workspace, then run sshd in the foreground.
set -eu
mkdir -p /etc/devenv/hostkeys
[ -f /etc/devenv/hostkeys/ssh_host_ed25519_key ] || ssh-keygen -q -t ed25519 -N "" -f /etc/devenv/hostkeys/ssh_host_ed25519_key
chmod 600 /etc/devenv/hostkeys/ssh_host_ed25519_key
mkdir -p /home/agent/workspace /home/agent/.npm-global
chown -R agent:agent /home/agent 2>/dev/null || true
exec /usr/sbin/sshd -D -e
