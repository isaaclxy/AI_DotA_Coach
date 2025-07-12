# Security Policy

## Reporting Security Vulnerabilities

We take security seriously. If you discover a security vulnerability in DotA Coach, please report it responsibly.

### 🔒 Private Reporting (Recommended)

Use GitHub's private security advisory feature:
1. Go to the **Security** tab of this repository
2. Click **"Report a vulnerability"**
3. Provide detailed information about the vulnerability
4. We'll respond within 48 hours and work with you on coordinated disclosure

### 📧 Alternative Contact

If you prefer email communication, you can reach the maintainer through their GitHub profile contact information.

## Security Best Practices

### 🔑 API Keys and Credentials

**OpenDota API Keys:**
- ✅ **DO**: Store API keys in `.env` files only
- ✅ **DO**: Use the provided `.env.example` template
- ❌ **NEVER**: Commit real API keys to the repository
- ❌ **NEVER**: Hardcode API keys in source code
- 🔄 **If exposed**: Regenerate your OpenDota API key immediately

**Environment Variables:**
```bash
# ✅ Correct - in .env file (gitignored)
OPENDOTA_API_KEY=your_actual_key_here

# ❌ Wrong - hardcoded in source
api_key = "OD-1234567890abcdef"  # Never do this!
```

### 📊 Data Security

**Match Data Privacy:**
- Match data from OpenDota API is public information
- Downloaded match files contain player statistics but no personal identifiers
- State tracking files (`downloaded_matches.csv`, `parse_backlog.csv`) contain match IDs only
- No sensitive player information is stored locally

**Local Storage:**
- All data files are stored locally and not transmitted elsewhere
- Match JSON files contain publicly available game statistics
- Configuration files may contain API keys - ensure proper `.env` usage

### 💻 Development Security

**AI-Assisted Development:**
- Code generated through AI assistance should be reviewed for security implications
- Avoid sharing sensitive configuration or API keys in AI prompts
- Review AI-generated code for potential security vulnerabilities

**Git Repository Security:**
- `.env` files are gitignored to prevent credential exposure
- Personal documentation (`personal_docs/`) is gitignored to protect private notes
- Experimental scripts (`scripts/temp/`) are gitignored
- Clean git history established to prevent exposure of historical sensitive data

**Dependencies:**
- Regularly update Python packages: `pip install -r requirements.txt --upgrade`
- Monitor for security advisories in ML/AI packages (pandas, scikit-learn, requests)
- Virtual environment isolates dependencies from system Python

## Security Checklist

Before contributing or deploying, verify:

- [ ] No hardcoded API keys or credentials in source code
- [ ] `.env` file exists and contains all required configuration
- [ ] `.env` file is not tracked in git (should be gitignored)
- [ ] All API keys are stored as environment variables only
- [ ] Dependencies are up to date with security patches
- [ ] No sensitive data in git commit history
- [ ] Personal documentation remains in gitignored directories

## Project-Specific Security Considerations

### Current Implementation (Phase 1)
- **API Integration**: Secure OpenDota API key management
- **Data Collection**: Public match data only, no private player information
- **Local Processing**: All computation happens locally, no external data transmission

### Future Considerations
As the project evolves to include real-time features, additional security considerations will be documented here.

## Dependency Security

**Critical Dependencies:**
- `requests` - HTTP library for API calls
- `pandas` - Data processing (handle with care for large datasets)
- `scikit-learn` - ML framework (model security considerations)

**Security Updates:**
```bash
# Check for security advisories
pip audit

# Update all dependencies
pip install -r requirements.txt --upgrade
```

## Security Philosophy

**Learning Project Approach:**
- This is a personal learning project built through AI-assisted development
- Security practices are implemented as learning opportunities
- Balance between educational goals and security best practices
- Open source development with transparent security policies

**Responsible Development:**
- No malicious use of gaming data or APIs
- Respect for OpenDota API terms of service
- Privacy-conscious handling of public match statistics
- Clean development practices for educational value

---

**Security is a shared responsibility.** Whether you're contributing code, reporting issues, or using this project as a learning resource, following these security practices helps maintain a safe development environment for everyone.

*If you have questions about security practices or need clarification on any of these guidelines, feel free to open an issue or start a discussion.*