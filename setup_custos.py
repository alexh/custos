#!/usr/bin/env python3
"""
Setup script for Custos Server
Generates secure tokens and initializes configuration
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from datetime import datetime


def generate_token():
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(32)


def hash_token(token):
    """Create SHA256 hash of token"""
    return hashlib.sha256(token.encode()).hexdigest()


def setup_custos_server():
    """Initialize custos server configuration"""
    base_dir = Path("/opt/custos")
    config_file = base_dir / "config.json"
    
    # Use home directory if not root, otherwise /root
    if os.geteuid() == 0:
        token_file = Path("/root/custos-tokens.txt")
    else:
        token_file = Path.home() / "custos-tokens.txt"
    
    # Check if already configured
    if config_file.exists():
        print("⚠️  Custos server already configured!")
        print("To reset, delete /opt/custos/config.json first")
        return False
    
    print("🔐 Custos Server Setup")
    print("======================")
    
    # Create directory
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate tokens
    print("🔑 Generating secure access tokens...")
    tokens = {
        "primary": generate_token(),
        "emergency": generate_token(),
        "setup": generate_token()
    }
    
    # Create configuration
    config = {
        "tokens": {
            name: hash_token(token) 
            for name, token in tokens.items()
        },
        "setup_complete": False,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(config_file, 0o600)
    
    # Save tokens for user
    with open(token_file, 'w') as f:
        f.write("CUSTOS SERVER TOKENS\n")
        f.write("===================\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write(f"Primary Token (for client):\n{tokens['primary']}\n\n")
        f.write(f"Emergency Token (for admin):\n{tokens['emergency']}\n\n")
        f.write(f"Setup Token (one-time use):\n{tokens['setup']}\n\n")
        f.write("IMPORTANT: Save these tokens in your password manager NOW!\n")
        f.write("This file will be deleted after setup completes.\n")
    
    os.chmod(token_file, 0o600)
    
    print("✅ Configuration created")
    print(f"\n🔑 Tokens saved to: {token_file}")
    print("\n⚠️  IMPORTANT: Save these tokens NOW!")
    print("They will not be shown again.\n")
    
    return True


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ This script must be run as root")
        exit(1)
    
    if setup_custos_server():
        print("Next steps:")
        print("1. cat /root/custos-tokens.txt")
        print("2. Save tokens to password manager")
        print("3. Install and start the custos service")