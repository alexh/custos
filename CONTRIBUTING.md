# Contributing to Custos

Thank you for your interest in contributing to Custos! We welcome contributions from the community and are grateful for your help in making this project better.

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be respectful and constructive in all interactions.

## Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/custos.git
   cd custos
   ```
3. **Set up development environment**:
   ```bash
   ./dev-setup.sh
   source venv/bin/activate
   ```
4. **Run tests** to ensure everything works:
   ```bash
   python custos_server.py &
   ./test-api.sh
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add: brief description of what you added"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub

## What We're Looking For

### 🔐 Security Improvements
- Enhanced authentication mechanisms
- Better encryption methods
- Security vulnerability fixes
- Security audit findings

### 🚀 Performance Enhancements
- Database optimization
- Memory usage improvements
- Response time optimizations
- Caching mechanisms

### 📱 User Experience
- Mobile interface improvements
- Better error messages
- API usability enhancements
- Documentation improvements

### 🧪 Testing & Quality
- Unit tests
- Integration tests
- Load testing
- Code quality improvements

### 📖 Documentation
- API documentation
- Setup guides
- Use case examples
- Troubleshooting guides

## Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Security Guidelines
- Never log sensitive data (tokens, passwords, etc.)
- Use secure defaults
- Validate all inputs
- Follow principle of least privilege

### API Design
- RESTful endpoints
- Consistent error responses
- Proper HTTP status codes
- Clear JSON structure

## Testing

All contributions should include appropriate tests:

### Running Tests
```bash
# Start the server
python custos_server.py &

# Run API tests
./test-api.sh

# For manual testing
curl http://localhost:5555/health
```

### Test Coverage
- API endpoint tests
- Authentication tests
- Error handling tests
- Security boundary tests

## Documentation

When contributing:
- Update README.md if adding new features
- Add inline code comments for complex logic
- Update API documentation for new endpoints
- Include examples in commit messages

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Commit messages are clear

### PR Description Template
```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Security improvement
- [ ] Documentation update
- [ ] Performance enhancement

## Testing
- [ ] Tested locally
- [ ] API tests pass
- [ ] No new security vulnerabilities

## Notes
Any additional context or considerations
```

### Review Process
1. **Automated checks** run on all PRs
2. **Code review** by maintainers
3. **Security review** for security-related changes
4. **Merge** after approval

## Issue Reporting

### Bug Reports
Include:
- Operating system and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs (redacted)

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Potential impact on security

### Security Issues
**DO NOT** create public issues for security vulnerabilities.
Email security concerns privately to the maintainers.

## Release Process

Releases follow semantic versioning:
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, security patches

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit history

## Questions?

- Check existing [Issues](https://github.com/alexh/custos/issues)
- Start a [Discussion](https://github.com/alexh/custos/discussions)
- Review the [Wiki](https://github.com/alexh/custos/wiki)

Thank you for contributing to Custos! 🔐