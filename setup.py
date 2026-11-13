from setuptools import find_packages, setup

setup(
    name="procuregatebench",
    version="0.1.0",
    description="Process-gate and red-flag calibration benchmark for agentic procurement triage",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.9",
    install_requires=[],
    entry_points={"console_scripts": ["procuregatebench=procuregatebench.cli:main"]},
)
