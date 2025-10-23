# Contributing to ProbePilot 🛩️

Thank you for your interest in contributing to ProbePilot! We're excited to work with you to build the best eBPF observability platform.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Linux kernel 4.4+ (for eBPF development)
- Git

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/probepilot.git`
3. Follow the [Development Setup Guide](docs/DEVELOPMENT.md)
4. Create a feature branch: `git checkout -b feature/amazing-feature`

## 📋 How to Contribute

### 🐛 Bug Reports
Found a bug? Please [create an issue](https://github.com/jedi132000/probepilot/issues/new?template=bug_report.md) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### ✨ Feature Requests
Have an idea? [Create a feature request](https://github.com/jedi132000/probepilot/issues/new?template=feature_request.md) with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation approach
- Any mockups or examples

### 🔧 Code Contributions

#### Pull Request Process
1. **Create an issue** first to discuss major changes
2. **Fork and branch** from the main branch
3. **Write tests** for new functionality
4. **Follow code style** guidelines (see below)
5. **Update documentation** as needed
6. **Submit a pull request** with clear description

#### Code Style Guidelines

**Python Code:**
```bash
# Format with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy backend/ frontend/
```

**Commit Messages:**
Use conventional commit format:
```
type(scope): description

feat(frontend): add real-time probe deployment
fix(backend): resolve memory leak in metrics collection
docs(readme): update quick start instructions
```

#### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or clearly documented)
- [ ] Security considerations addressed

## 🏗️ Project Structure

```
probepilot/
├── frontend/          # Gradio web interface
├── backend/           # FastAPI backend
├── probes/           # eBPF probe implementations
├── docs/             # Documentation
├── tests/            # Test suites
└── scripts/          # Utility scripts
```

## 🧪 Testing

### Running Tests
```bash
# All tests
npm run test

# Backend tests only
cd backend && pytest

# Frontend tests only  
cd frontend && pytest

# With coverage
pytest --cov=app tests/
```

### Writing Tests
- Write unit tests for all new functions
- Add integration tests for API endpoints
- Include end-to-end tests for critical workflows
- Mock external dependencies

## 📚 Documentation

### Types of Documentation
- **Code comments**: Explain complex logic
- **Docstrings**: Document functions and classes
- **README updates**: Keep setup instructions current
- **Architecture docs**: Document design decisions
- **API docs**: Keep OpenAPI specs updated

### Documentation Style
- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep aviation theme consistent

## 🎯 Contribution Areas

### High Priority
- eBPF probe implementations
- Backend API endpoints
- Gradio UI components
- Performance optimizations
- Documentation improvements

### Good First Issues
Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`
- `frontend`
- `backend`

### Advanced Contributions
- eBPF kernel programming
- Real-time data processing
- AI/ML integration
- Performance optimization
- Security enhancements

## 🔒 Security

### Reporting Security Issues
**Do not open public issues for security vulnerabilities.**

Instead, email: security@probepilot.dev

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fixes (if any)

### Security Guidelines
- Validate all inputs
- Use parameterized queries
- Implement proper authentication
- Follow OWASP guidelines
- Scan dependencies regularly

## 🏆 Recognition

### Contributors
All contributors are recognized in:
- README contributors section
- Release notes
- Project documentation

### Contribution Types
We recognize various contribution types:
- 💻 Code
- 📖 Documentation
- 🐛 Bug reports
- 💡 Ideas
- 🎨 Design
- 🔍 Testing

## 📞 Getting Help

### Community Channels
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat (coming soon)

### Maintainer Contact
- GitHub: @jedi132000
- Email: maintainers@probepilot.dev

## 📜 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Standards
**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement
Report unacceptable behavior to: conduct@probepilot.dev

## 📋 Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent production fixes

### Release Process
1. Features merge into `develop`
2. Release candidates cut from `develop`
3. Testing and bug fixes
4. Merge to `main` and tag release
5. Deploy to production

## 🎉 Thank You!

Your contributions make ProbePilot better for everyone. Whether you're fixing a typo, adding a feature, or reporting a bug, we appreciate your involvement in building the future of eBPF observability!

---

*Ready to take flight with ProbePilot development? Let's build something amazing together! 🛩️*