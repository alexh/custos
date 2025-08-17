<div align="center">

# <img src="guard_white.png" width="40" height="40"> Custos 🔐 <img src="guard_white_reversed.png" width="40" height="40">

[![Test](https://github.com/alexh/custos/actions/workflows/test.yml/badge.svg)](https://github.com/alexh/custos/actions/workflows/test.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A lightweight, secure token management service for distributed systems. Built with Flask and designed for simplicity and security.*

</div>

## Features

- **Secure Token Storage** - Encrypted storage with SHA256 hashing
- **Access Control** - Role-based authentication (primary, emergency, setup)
- **Web Interface** - Mobile-friendly control panel
- **Lock/Unlock** - Temporarily disable token access
- **Emergency Reset** - Secure data destruction capabilities
- **REST API** - Simple HTTP endpoints for integration

## Quick Start

### One-line Installation

```bash
curl -sSL https://raw.githubusercontent.com/alexh/custos/main/install.sh | bash
```

### Manual Installation

```bash
git clone https://github.com/alexh/custos.git
cd custos
sudo ./install_custos.sh
```

## Usage

After installation, Custos runs on port 80 and provides:

- **Web Interface**: `http://your-server-ip/`
- **API Endpoints**: RESTful API for token management
- **Control Panel**: Mobile-friendly admin interface

### API Endpoints

```bash
# Store data
PUT /data/{id}
{
  "data": "your-secure-data"
}

# Retrieve data
GET /data/{id}
Authorization: Bearer your-primary-token

# Lock service (prevent data access)
POST /lock
Authorization: Bearer your-emergency-token

# Emergency reset (destroy all data)
DELETE /wipe
Authorization: Bearer your-emergency-token
{
  "confirm": "DESTROY_ALL_KEYS"
}
```

## Configuration

Custos generates secure tokens during setup:

- **Primary Token**: For normal data operations
- **Emergency Token**: For admin operations (lock/wipe)
- **Setup Token**: One-time use for initial configuration

Tokens are saved to `/root/custos-tokens.txt` during installation.

## Security

- All tokens are SHA256 hashed before storage
- Data is stored with restricted file permissions (600)
- Emergency wipe overwrites files before deletion
- Role-based access control prevents privilege escalation
- No plaintext secrets in logs or memory dumps

## Use Cases

- **API Key Management**: Secure storage for service credentials
- **Configuration Distribution**: Centralized config for microservices
- **Secrets Management**: Lightweight alternative to Vault
- **Development Tools**: Secure token distribution for dev teams
- **IoT Device Auth**: Credential management for edge devices

## Requirements

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker (for testing)
- Flask and Gunicorn (installed automatically)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  Custos Server  │───▶│  Token Storage  │
│                 │    │                 │    │                 │
│ - API requests  │    │ - Authentication│    │ - Encrypted     │
│ - Token auth    │    │ - Access control│    │ - File perms    │
│ - REST calls    │    │ - Rate limiting │    │ - Secure wipe   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Production Deployment

For production use, consider:

1. **SSL/TLS**: Use nginx for HTTPS termination
2. **Firewall**: Restrict access to necessary ports only
3. **Monitoring**: Set up logging and health checks
4. **Backup**: Regular backup of configuration (not tokens)
5. **Updates**: Keep dependencies current

## Development

### Local Development

```bash
git clone https://github.com/alexh/custos.git
cd custos
make setup     # Install dependencies and generate tokens
make dev       # Start development server
```

### Docker Development

```bash
# Build and run with docker-compose
docker-compose up --build

# Or manually
docker build -t custos .
docker run -p 5555:5555 custos
```

### Testing

Run the complete test suite with one command:

```bash
make test
```

This will:
- Start Docker containers
- Wait for server to be ready
- Extract tokens automatically
- Run pytest test suite
- Clean up containers

For individual commands:
```bash
make help      # Show all available commands
make install   # Install dependencies only
make setup     # Install deps + configure server
make dev       # Run development server
make clean     # Clean up temp files
```

## Contributing

Contributions welcome! Please read our [contributing guidelines](CONTRIBUTING.md) and submit pull requests for any improvements.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of all contributors.

## License

MIT License - see LICENSE file for details.

## Support

- 📖 Documentation: See `/docs` directory
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Contact: See GitHub profile

---

**Note**: Custos is designed for security-conscious applications. Always review the code and test thoroughly before production use.