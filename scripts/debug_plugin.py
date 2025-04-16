#!/usr/bin/env python3
"""
Debug script to test MkDocs plugin loading.
"""

import sys
import importlib.metadata
from mkdocs.config import load_config
from mkdocs.plugins import get_plugin_logger

def main():
    print("Python version:", sys.version)
    print("Python path:", sys.path)
    
    # Check if mkdocs-click is installed
    try:
        dist = importlib.metadata.distribution("mkdocs-click")
        print("\nmkdocs-click installation found:")
        print(f"Version: {dist.version}")
        print(f"Location: {dist.locate_file('')}")
    except importlib.metadata.PackageNotFoundError:
        print("\nERROR: mkdocs-click not found in Python environment")
        return 1
    
    # Try to load the plugin directly
    try:
        plugin_module = importlib.import_module("mkdocs_click")
        print("\nPlugin module loaded successfully")
        print(f"Plugin module location: {plugin_module.__file__}")
    except ImportError as e:
        print(f"\nERROR: Could not import plugin module: {e}")
        return 1
    
    # Try to load the config
    try:
        config = load_config("mkdocs.yml")
        print("\nMkDocs config loaded successfully")
        print("Plugins in config:", config.get("plugins", []))
    except Exception as e:
        print(f"\nERROR: Could not load MkDocs config: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 