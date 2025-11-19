#!/usr/bin/env python3
import re
from pathlib import Path

def bump_version(version_str):
    major, minor, patch = map(int, version_str.split('.'))
    return f"{major}.{minor}.{patch + 1}"

def update_file(file_path, pattern, version_group_index=1):
    path = Path(file_path)
    if not path.exists():
        print(f"Warning: {file_path} not found.")
        return None

    content = path.read_text(encoding='utf-8')
    match = re.search(pattern, content)
    
    if match:
        current_version = match.group(version_group_index)
        new_version = bump_version(current_version)
        new_content = content.replace(match.group(0), match.group(0).replace(current_version, new_version))
        path.write_text(new_content, encoding='utf-8')
        print(f"Updated {file_path}: {current_version} -> {new_version}")
        return new_version
    else:
        print(f"Warning: Version pattern not found in {file_path}")
        return None

def main():
    # Update app/__init__.py
    # Pattern: __version__ = "1.0.0"
    version = update_file('app/__init__.py', r'__version__\s*=\s*"([^"]+)"')
    
    if version:
        # Update app/core/config.py
        # Pattern: api_version: str = "1.0.0"
        update_file('app/core/config.py', r'api_version:\s*str\s*=\s*"([^"]+)"')

if __name__ == "__main__":
    main()


