#!/bin/bash
# Install Vigil Key Server as a service

set -e

echo "🔐 Installing Vigil Key Server..."

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

# Create directories
mkdir -p /opt/vigil-keys
cd /opt/vigil-keys

# Copy files
cp key_server.py /opt/vigil-keys/
cp setup_key_server.py /opt/vigil-keys/
chmod +x setup_key_server.py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install flask gunicorn

# Run setup if needed
if [ ! -f "config.json" ]; then
    echo "🔑 Running initial setup..."
    python3 setup_key_server.py
fi

# Create systemd service
cat > /etc/systemd/system/vigil-key-server.service <<EOF
[Unit]
Description=Vigil Key Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vigil-keys
Environment="PATH=/opt/vigil-keys/venv/bin"
ExecStart=/opt/vigil-keys/venv/bin/gunicorn -w 1 -b 127.0.0.1:5555 key_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx reverse proxy (optional for SSL)
cat > /etc/nginx/sites-available/vigil-key-server <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5555;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/vigil-key-server /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Start service
systemctl daemon-reload
systemctl enable vigil-key-server
systemctl start vigil-key-server

echo ""
echo "✅ Key server installed!"
echo ""
echo "📱 Access at: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Check status: systemctl status vigil-key-server"
echo "View logs: journalctl -fu vigil-key-server"