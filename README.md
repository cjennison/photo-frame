# Photo Frame Application

This application is a digital photo frame designed to run on Raspberry Pi. It downloads and displays photos and videos, offers a slideshow mode, and supports updates from Azure Blob Storage.

---

## Features

- Automatically fetch photos and videos from Azure Blob Storage.
- Display media in fullscreen mode with UI controls.
- Support for manual and automatic updates via GitHub.
- Python virtual environment for dependency management.
- Autostarts on Raspberry Pi boot.

---

## Setup Instructions

### Prerequisites

Ensure your Raspberry Pi has the following installed:

- Python 3.x
- Git
- curl
- unzip
- A configured Azure Blob Storage SAS token (if required for media fetching).

---

### Step 1: Set Up SSH Access to the Raspberry Pi

1. **Enable SSH on the Raspberry Pi**:

   - Run the following command on the Raspberry Pi to enable SSH:
     ```bash
     sudo raspi-config
     ```
   - Navigate to **Interface Options** > **SSH** and enable it.

2. **Find the Raspberry Pi's IP Address**:

   - Run the following command to get the IP address:
     ```bash
     hostname -I
     ```
   - Note the IP address (e.g., `192.168.1.100`).

3. **Access the Raspberry Pi via SSH from Your PC**:

   - Use an SSH client (e.g., Terminal on macOS/Linux or PuTTY on Windows) to connect:
     ```bash
     ssh pi@<your-pi-ip>
     ```
   - Replace `<your-pi-ip>` with the IP address of your Raspberry Pi.
   - Default username: `pi`
   - Default password: `raspberry` (if unchanged).

4. **Optional: Set Up SSH Key-Based Authentication**:
   - On your PC, generate an SSH key (if you don’t already have one):
     ```bash
     ssh-keygen -t rsa -b 4096
     ```
   - Copy the key to the Raspberry Pi:
     ```bash
     ssh-copy-id pi@<your-pi-ip>
     ```
   - You can now log in without a password.

---

### Step 2: Clone and Run the Setup Script

1. SSH into your Raspberry Pi:

   ```bash
   ssh pi@<your-pi-ip>
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/photo_frame.git
   cd photo_frame
   ```

3. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
   - This script installs required dependencies, sets up a Python virtual environment, and starts the application.

---

### Step 3: Running the Application

After running the setup script:

- The application will start automatically.
- To restart manually:
  ```bash
  cd photo_frame
  source venv/bin/activate
  python3 main.py
  deactivate
  ```

---

### Step 4: Autostart on Boot

1. Create a systemd service for the application:

   ```bash
   sudo nano /etc/systemd/system/photo_frame.service
   ```

   Add the following content:

   ```ini
   [Unit]
   Description=Photo Frame Application
   After=network.target

   [Service]
   ExecStart=/home/pi/photo_frame/run.sh
   WorkingDirectory=/home/pi/photo_frame
   Restart=always
   User=pi
   Environment=DISPLAY=:0

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable photo_frame
   sudo systemctl start photo_frame
   ```

3. Check the status:
   ```bash
   sudo systemctl status photo_frame
   ```

---

## Updating the Application

To update the application:

1. Fetch the latest code:

   ```bash
   cd photo_frame
   git pull
   ```

2. Restart the service:
   ```bash
   sudo systemctl restart photo_frame
   ```

---

## Notes

- **Environment Variables**: Store sensitive information like Azure SAS tokens in a `.env` file. Example:

  ```
  SAS_TOKEN="?sv=2022-11-02&ss=bfqt&srt=co&sp=rw"
  ```

- **Requirements**: Ensure `requirements.txt` lists all Python dependencies.

---

## Troubleshooting

1. **Application Not Starting**:

   - Check logs:
     ```bash
     sudo journalctl -u photo_frame
     ```
   - Check end of logs:
     ```bash
     sudo journalctl -u photo_frame -n 100
     ```

2. **Media Not Loading**:
   - Ensure Azure SAS token is valid and has the correct permissions.
   - Verify network connectivity.

---

For further assistance, please reach out to the repository maintainer.
