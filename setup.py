"""
Setup configuration for todo-mcp package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="todo-mcp",
    version="0.1.0",
    author="Jake",
    description="Multi-workspace task coordinator with subtask/dependency support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakez-gh/todo-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        # minimal dependencies for now
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "todo-mcp=todo_mcp.cli:main",
        ],
    },
)