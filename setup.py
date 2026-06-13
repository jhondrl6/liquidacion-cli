#!/usr/bin/env python
# -*- coding: ascii -*-

"""
Setup script for the Colombia Payroll Settlement System 2025.
Installation configuration with pip, dependency definition and entry points.

Author: Development Team
Date: 2025-11-04
Version: 1.0.0
"""

import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

# Project path
here = Path(__file__).parent

# Read README.md content for long description
with open(here / "README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements.txt content for production dependencies
with open(here / "requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read requirements-dev.txt content for development dependencies
with open(here / "requirements-dev.txt", "r", encoding="utf-8") as f:
    dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]


class PostInstallCommand(install):
    """Post-installation command for initial system configuration."""
    
    def run(self):
        # Execute normal installation
        install.run(self)
        
        # Create required directories
        self.create_required_directories()
        
        # Show successful installation message
        self.display_success_message()
    
    def create_required_directories(self):
        """Creates required directories for system operation."""
        required_dirs = [
            "params",
            "audit/logs",
            "audit/trails",
            "audit/reports",
            "output",
            "logs",
            "templates"
        ]
        
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def display_success_message(self):
        """Shows a success message after installation."""
        success_message = '''
================================================================================
||                                                                            ||
||                SUCCESS - Colombia Payroll Settlement System 2025!          ||
||                                                                            ||
||  To start using the system:                                                ||
||     python -m liquidator.cli --help                                       ||
||                                                                            ||
||  Documentation:                                                            ||
||     - User guide: docs/user_guide.md                                      ||
||     - Developer guide: docs/developer_guide.md                            ||
||                                                                            ||
||  Initial configuration:                                                    ||
||     - Legal parameters: params/2025.json                                  ||
||     - System configuration: config/default_config.yaml                    ||
||                                                                            ||
================================================================================
        '''
        print(success_message)


setup(
    name="colombia_payroll_settlement",
    version="1.0.0",
    description="Colombia Payroll Settlement System 2025 - Calculation of social benefits and legal compliance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Payroll Settlement Development Team",
    author_email="development@company.com",
    url="https://github.com/user/colombia_payroll_settlement",
    license="MIT",
    
    # Packages to include
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "pdf": ["weasyprint>=59.0"],
        "excel": ["openpyxl>=3.0.0"]
    },
    
    # CLI entry points
    entry_points={
        "console_scripts": [
            "settle=liquidator.cli.main:main",
            "settle-compliance=scripts.validate_compliance:main",
            "settle-update-params=scripts.update_params:main",
            "settle-generate-tests=scripts.generate_test_data:main"
        ]
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    
    # Keywords
    keywords="payroll,colombia,settlement,social benefits,severance,bonus,vacations,indemnification,legal compliance",
    
    # Custom commands
    cmdclass={
        "install": PostInstallCommand
    },
    
    # Additional metadata
    project_urls={
        "Documentation": "https://github.com/user/colombia_payroll_settlement/docs",
        "Source Code": "https://github.com/user/colombia_payroll_settlement",
        "Issues": "https://github.com/user/colombia_payroll_settlement/issues"
    },
    
    # Python requirements
    python_requires=">=3.8",
    
    # Additional data files
    package_data={
        "liquidator": [
            "py.typed",
            "templates/*.md",
            "templates/*.css",
            "templates/partials/*.md"
        ]
    },
    
    # Additional scripts
    scripts=[
        "scripts/update_params.py",
        "scripts/validate_compliance.py",
        "scripts/generate_test_data.py"
    ]
)