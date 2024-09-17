#!/bin/bash

# Define the download URL and file names
DOWNLOAD_URL="https://github.com/vvnocode/vpspeek/releases/latest/download/vpspeek"
DOWNLOAD_FILE="download_vpspeek"
TARGET_FILE="vpspeek"
SERVICE_NAME="vpspeek"

# Number of retries
RETRIES=3

# Download the file with retries
attempt=0
while [ $attempt -lt $RETRIES ]; do
    echo "Attempting to download file... (Attempt $((attempt + 1))/$RETRIES)"
    wget -O $DOWNLOAD_FILE $DOWNLOAD_URL

    if [ $? -eq 0 ]; then
        echo "Download successful."
        break
    else
        echo "Download failed."
        attempt=$((attempt + 1))
        if [ $attempt -eq $RETRIES ]; then
            echo "Download failed after $RETRIES attempts. Exiting."
            exit 1
        fi
    fi
done

# Check if the service exists and stop it if running
if systemctl list-units --type=service | grep -q "$SERVICE_NAME"; then
    echo "Stopping $SERVICE_NAME service..."
    systemctl stop $SERVICE_NAME
fi

# Remove old vpspeek file if it exists
if [ -f "$TARGET_FILE" ]; then
    echo "Removing old $TARGET_FILE file..."
    rm -f $TARGET_FILE
fi

# Rename downloaded file to vpspeek and make it executable
mv $DOWNLOAD_FILE $TARGET_FILE
chmod +x $TARGET_FILE
echo "Renamed $DOWNLOAD_FILE to $TARGET_FILE and made it executable."

# Create a systemd service file if it doesn't exist
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
if [ ! -f "$SERVICE_PATH" ]; then
    echo "Creating systemd service file for $SERVICE_NAME..."
    cat <<EOL > $SERVICE_PATH
[Unit]
Description=VPSPeek Service
After=network.target

[Service]
ExecStart=$(pwd)/$TARGET_FILE
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOL

    # Reload systemd, enable service, and start it
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
fi

# Start the service
echo "Starting $SERVICE_NAME service..."
systemctl start $SERVICE_NAME

echo "$SERVICE_NAME installed and started successfully."
