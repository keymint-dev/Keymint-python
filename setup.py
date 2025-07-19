from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="keymint",
    version="0.1.0",
    author="Keymint",
    author_email="admin@keymint.dev",
    description="A Python SDK for the KeyMint API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keymint-dev/keymint-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ],
)
