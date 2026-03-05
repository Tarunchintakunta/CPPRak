"""Setup script for qr_ticket_manager package."""

from setuptools import setup, find_packages

setup(
    name="qr_ticket_manager",
    version="1.0.0",
    author="Rakshan",
    author_email="25180754@student.uwa.edu.au",
    description="A library for generating and validating QR-coded event tickets",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "qrcode>=7.0",
        "Pillow>=9.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
