login_monitor.py

A small cross-platform login/logout monitor using `psutil.users()`.

Features
- Polls user sessions and detects new/removed sessions (login/logout).
- Writes events as JSON lines to stdout and to `logs/login_monitor.log` by default.
- Simple, no external system dependencies besides `psutil`.

Quick start

1. Install dependency:

    pip install -r requirements.txt

2. Run monitor:

    python target/login_monitor.py --interval 2 --logfile logs/login_monitor.log

Sample systemd unit (Linux)

Create `/etc/systemd/system/login-monitor.service` with:

[Unit]
Description=Login Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/Documents/Hackathon2026
ExecStart=/usr/bin/python3 /home/youruser/Documents/Hackathon2026/target/login_monitor.py --interval 2 --logfile /home/youruser/Documents/Hackathon2026/logs/login_monitor.log
Restart=on-failure

[Install]
WantedBy=multi-user.target

Then enable and start:

    sudo systemctl daemon-reload
    sudo systemctl enable --now login-monitor

Notes
- On Windows, run the script from a persistent process (Task Scheduler, or a background Python process).
- psutil may require administrative privileges for some session info on some systems.
- This script uses polling; it's intentionally simple. For advanced auditing, integrate with OS audit subsystems (auditd on Linux, Windows Event Log APIs).
