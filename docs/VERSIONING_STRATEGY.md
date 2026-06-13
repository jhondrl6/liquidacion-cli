# Versioning Strategy
## Colombia Payroll Settlement System 2025

This document outlines the versioning strategy and release cycle for the settlement system.

---

## Version Policy

### Semantic Versioning (SemVer)

This project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):

- **MAJOR.MINOR.PATCH** format (e.g., 1.0.0, 1.1.2, 2.0.0)
- **MAJOR**: Incompatible API changes or significant new functionality
- **MINOR**: New functionality in a backwards compatible manner  
- **PATCH**: Backwards compatible bug fixes

### Version Examples

| Version | Release Type | Description |
|---------|-------------|-------------|
| 1.0.0 | Major | Initial production release |
| 1.1.0 | Minor | New output formats (Excel export) |
| 1.1.1 | Patch | Bug fix in indemnization calculation |
| 2.0.0 | Major | Major architectural changes or 2026 parameter update |

---

## Release Schedule

### Major Releases (Annual)
- **Timing**: January 15th each year
- **Content**: 
  - Updated legal parameters for new year
  - Major feature additions
  - Architecture improvements
- **Version bump**: Major version increment (e.g., 1.0.0 → 2.0.0)

### Minor Releases (Quarterly)
- **Timing**: January 15th, April 15th, July 15th, October 15th
- **Content**:
  - New features and improvements
  - Compliance enhancements
  - Performance optimizations
- **Version bump**: Minor version increment (e.g., 1.0.0 → 1.1.0)

### Patch Releases (As Needed)
- **Timing**: Within 30 days of critical bug discovery
- **Content**:
  - Bug fixes
  - Security patches
  - Critical compliance updates
- **Version bump**: Patch version increment (e.g., 1.0.0 → 1.0.1)

---

## Release Channels

### Stable Channel
- **Version**: Latest stable release (e.g., 1.0.0)
- **Usage**: Production environments
- **Updates**: Minor and patch releases only
- **Stability**: Fully tested and validated

### Development Channel
- **Version**: Main branch (v1.0.0-dev or v1.1.0-dev)
- **Usage**: Development and testing
- **Updates**: Continuous integration
- **Stability**: May contain bugs and incomplete features

### Security Channel
- **Version**: Security patches on latest stable version (e.g., 1.0.1-security)
- **Usage**: Critical security updates
- **Updates**: As needed (within 30 days of vulnerability)
- **Stability**: Security-only patches, backward compatible

---

## Version Number Planning

### 1.0.x Series (2025)
- **1.0.0**: Initial production release (2025-11-04)
- **1.0.1**: Bug fixes and stabilizations
- **1.0.2**: Security patches and compliance updates

### 1.1.x Series (Q1-Q2 2025)
- **1.1.0**: Excel export, web API, enhanced validation
- **1.1.1**: Performance optimizations
- **1.1.2**: Enhanced security features

### 1.2.x Series (Q3-Q4 2025)
- **1.2.0**: Advanced reporting, batch processing
- **1.2.1**: Compliance updates for new legal changes
- **1.2.2**: End-of-year improvements

### 2.0.x Series (2026)
- **2.0.0**: 2026 parameters, architecture overhaul, new features

---

## Breaking Changes Policy

### What Constitutes a Breaking Change?

Breaking changes require a MAJOR version increment:

1. **API Changes**: Removal or modification of public interfaces
2. **Data Format Changes**: Changes to JSON output structure
3. **Parameter Updates**: Changes to parameter file format
4. **Configuration Changes**: Changes to configuration file structure
5. **Dependency Changes**: Requiring newer Python versions or major library changes

### Breaking Change Examples

```python
# Minor (safe)
def calculate_cesantias(input_data):  # Existing function maintained
    # Enhanced implementation
    pass

# Major (breaking)    
def calculate_cesantias_v2(input_data):  # New function name
    pass
# OR
def calculate_cesantias(input_data, new_required_param):  # Required new parameter
    pass
```

### Backward Compatibility Goals

- **API Stability**: Maintain existing API across minor releases
- **Configuration Format**: Support for older config formats when possible
- **Parameter Files**: Migration utilities for outdated parameter files
- **JSON Format**: Maintain backward compatibility for at least 2 major versions

---

## Release Process

### Pre-Release Checklist

For all releases (especially major/minor):

1. **Code Quality**
   - [ ] All tests passing (85%+ coverage)
   - [ ] Code review complete
   - [ ] Documentation updated
   - [ ] Changelog updated

2. **Security Review**
   - [ ] Security audit completed
   - [ ] Vulnerability scan clean
   - [ ] Dependencies updated to latest secure versions

3. **Testing**
   - [ ] Unit tests updated and passing
   - [ ] Integration tests passing
   - [ ] End-to-end tests with real examples
   - [ ] Performance tests meeting benchmarks

4. **Compliance**
   - [ ] Legal compliance validation
   - [ ] Audit trail verification
   - [ ] Documentation audit complete

5. **Production Readiness**
   - [ ] Production configuration tested
   - [ ] Backup/restore procedures verified
   - [ ] Monitoring alerts configured
   - [ ] Rollback plan documented

### Release Steps

```bash
# 1. Create release branch
git checkout -b release/v1.1.0 main

# 2. Update version numbers
# - setup.py
# - config/default_config.yaml
# - Any other version references

# 3. Update changelog
git add CHANGELOG.md
git commit -m "Update changelog for v1.1.0"

# 4. Tag release
git tag -a v1.1.0 -m "Release v1.1.0: Feature updates and improvements"

# 5. Push to release
git push origin release/v1.1.0
git push origin v1.1.0

# 6. Create GitHub release
# Upload compiled packages
# Add release notes

# 7. Merge to main
git checkout main
git merge release/v1.1.0
git push origin main

# 8. Deploy to PyPI (if applicable)
twine upload dist/colombia_payroll_settlement-1.1.0-*.whl
```

---

## Parameter Release Strategy

### Annual Parameter Updates

Legal parameter updates require special handling:

1. **Release Timeline**
   - **November-December**: Development and testing of new parameters
   - **January 1st**: Official legal parameter update
   - **January 15th**: Software release with new parameters

2. **Version Strategy**
   - **Minor Release**: 1.0.0 → 1.1.0 (for parameter updates with features)
   - **Patch Release**: 1.0.0 → 1.0.1 (parameter updates only)
   - **Major Release**: 1.0.0 → 2.0.0 (significant architectural changes + parameters)

3. **Compatibility**
   - Support for previous year's parameters for 6 months
   - Migration utilities for parameter format changes
   - Clear documentation of parameter changes

### Parameter Versioning

```json
{
  "params_version": "2025-12-31",
  "vigencia_desde": "2025-01-01", 
  "vigencia_hasta": "2025-12-31",
  "parametros": {
    "SMMLV": 1423500,
    "AUXILIO_TRANS": 200000
  }
}
```

---

## Supporting Version Information

### Version Discovery

Users can discover installed version:

```bash
# CLI method
settle --version
# Output: colombia-payroll-settlement 1.0.0

# Python method
python -c "import liquidator; print(liquidator.__version__)"
# Output: 1.0.0

# Configuration method
python -c "import liquidator; print(liquidator.get_version())"
# Output: {'version': '1.0.0', 'build': '202511041200', 'git_sha': 'abc123def'}
```

### Build Information

Each release includes build metadata:

```python
{
    "version": "1.0.0",
    "build_date": "2025-11-04T12:00:00Z",
    "git_sha": "a1b2c3d4e5f6",
    "build_env": "production",
    "python_version": "3.11.5",
    "platform": "linux-x86_64"
}
```

---

## Long-Term Support (LTS)

### LTS Policy

- **LTS Releases**: Every 2nd major version (e.g., 2.0.0, 4.0.0)
- **Support Duration**: 3 years from release date
- **Update Types**: Security patches and critical bug fixes only
- **Backports**: Critical security fixes from newer versions

### Upgrade Paths

- **Current → Current**: Direct upgrade (e.g., 1.0.0 → 1.1.0)
- **LTS → Current**: Direct upgrade available (e.g., 2.0.0-LTS → 2.1.0)
- **LTS → Next LTS**: Upgrade path documented (e.g., 2.0.0-LTS → 4.0.0-LTS)

---

## Communication Strategy

### Release Notifications

### Channels
- **GitHub Releases**: Primary release announcement
- **Documentation**: Updated with release notes
- **Email Digest**: For major releases (subscribed users)
- **Blog Posts**: For major feature announcements

### Release Notes Format

Each release includes standardized release notes:

```markdown
# Release v1.0.0 (2025-11-04)

## 🎉 Major Features
- Complete settlement system implementation
- Production-ready monitoring and logging
- Security framework with threat detection

## 🐛 Bug Fixes
- Fixed calculation edge cases for partial periods
- Resolved PDF generation issues with special characters

## 🔒 Security Updates
- Enhanced input validation
- Fixed potential XSS vulnerability in output formatting

## ⚠️ Breaking Changes
- Changed JSON output format for compliance reporting
- Updated configuration file structure

## 📋 Requirements
- Python 3.8+ (was 3.8+)
- Updated dependencies (see requirements.txt)

## 🔄 Upgrade Instructions
[Detailed upgrade steps]

## 🙏 Acknowledgments
Community contributors and testers
```

---

## Future Roadmap

### Planned Features by Version

**v1.1.0 (Q1 2025)**
- Excel export functionality
- Web API REST endpoints
- Batch processing for multiple employees
- Enhanced reporting dashboard

**v1.2.0 (Q3 2025)**
- Database integration options
- Multi-tenant architecture
- Advanced reporting with trends
- Internationalization support

**v2.0.0 (January 2026)**
- 2026 legal parameter updates
- Microservices architecture
- Real-time compliance monitoring
- Advanced security features

---

## Maintenance Policy

### Support Windows

| Release Type | Support Duration | What's Included |
|---------------|------------------|------------------|
| Patch Releases | 12 months | Bug fixes only |
| Minor Releases | 18 months | Bug fixes + minor features |
| Major Releases | 24 months | Full support |
| LTS Releases | 36 months | Security fixes only |

### End-of-Life Process

1. **Warning Period**: 6 months notice before EOL
2. **Migration Guide**: Step-by-step upgrade instructions
3. **Security Only**: Continue security patches for 6 months post-EOL
4. **Archive**: Downloadable from GitHub with EOL notice

---

This versioning strategy ensures:

- **Predictability**: Users can plan for regular updates
- **Compatibility**: Backward compatibility is maintained where possible
- **Security**: Regular security updates and vulnerability fixes
- **Legal Compliance**: Timely parameter updates for changing regulations
- **Transparency**: Clear communication about changes and timelines

For questions about versioning or release planning, please contact the development team.
