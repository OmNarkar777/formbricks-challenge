#!/usr/bin/env python3
"""
Verification Script for Formbricks Challenge Solution

This script verifies the solution structure and requirements without
requiring external dependencies or a running Formbricks instance.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if filepath.exists():
        print(f"✓ {description}: {filepath.name}")
        return True
    else:
        print(f"✗ {description}: {filepath.name} - NOT FOUND")
        return False


def check_directory_structure():
    """Verify project directory structure"""
    print("\n=== Checking Directory Structure ===")
    project_root = Path(__file__).parent
    
    checks = [
        (project_root / "main.py", "Main entry point"),
        (project_root / "requirements.txt", "Python dependencies"),
        (project_root / "README.md", "Main documentation"),
        (project_root / "SETUP.md", "Setup guide"),
        (project_root / "TECHNICAL.md", "Technical documentation"),
        (project_root / "src" / "commands" / "up.py", "Up command"),
        (project_root / "src" / "commands" / "down.py", "Down command"),
        (project_root / "src" / "commands" / "generate.py", "Generate command"),
        (project_root / "src" / "commands" / "seed.py", "Seed command"),
        (project_root / "src" / "api" / "formbricks_client.py", "API client"),
        (project_root / "data" / "config" / "api_config.json.template", "Config template"),
    ]
    
    results = [check_file_exists(path, desc) for path, desc in checks]
    return all(results)


def check_command_structure():
    """Verify all four commands are implemented"""
    print("\n=== Checking Command Implementations ===")
    
    project_root = Path(__file__).parent
    commands = ["up", "down", "generate", "seed"]
    
    all_found = True
    for cmd in commands:
        cmd_file = project_root / "src" / "commands" / f"{cmd}.py"
        if cmd_file.exists():
            content = cmd_file.read_text()
            if "class" in content and "Command" in content and "execute" in content:
                print(f"✓ {cmd.capitalize()} command properly structured")
            else:
                print(f"✗ {cmd.capitalize()} command missing proper structure")
                all_found = False
        else:
            print(f"✗ {cmd.capitalize()} command file not found")
            all_found = False
    
    return all_found


def check_api_client():
    """Verify API client has required methods"""
    print("\n=== Checking API Client ===")
    
    project_root = Path(__file__).parent
    client_file = project_root / "src" / "api" / "formbricks_client.py"
    
    if not client_file.exists():
        print("✗ API client file not found")
        return False
    
    content = client_file.read_text()
    
    required_methods = [
        "verify_connection",
        "create_user",
        "create_survey",
        "create_response"
    ]
    
    all_found = True
    for method in required_methods:
        if f"def {method}" in content:
            print(f"✓ API method: {method}")
        else:
            print(f"✗ API method missing: {method}")
            all_found = False
    
    return all_found


def check_documentation():
    """Verify documentation completeness"""
    print("\n=== Checking Documentation ===")
    
    project_root = Path(__file__).parent
    
    docs = {
        "README.md": ["Installation", "Usage", "Requirements"],
        "SETUP.md": ["Prerequisites", "Installation"],
        "TECHNICAL.md": ["Architecture", "API"],
    }
    
    all_complete = True
    for doc_file, required_sections in docs.items():
        doc_path = project_root / doc_file
        if doc_path.exists():
            content = doc_path.read_text()
            missing = [s for s in required_sections if s.lower() not in content.lower()]
            if missing:
                print(f"⚠ {doc_file} missing sections: {', '.join(missing)}")
            else:
                print(f"✓ {doc_file} complete")
        else:
            print(f"✗ {doc_file} not found")
            all_complete = False
    
    return all_complete


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Formbricks Challenge Solution - Verification Script")
    print("=" * 60)
    
    structure_ok = check_directory_structure()
    commands_ok = check_command_structure()
    api_ok = check_api_client()
    docs_ok = check_documentation()
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", structure_ok),
        ("Command Implementation", commands_ok),
        ("API Client", api_ok),
        ("Documentation", docs_ok),
    ]
    
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check_name}: {status}")
    
    all_passed = all(result for _, result in checks)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All verification checks passed!")
        print("\nThe solution structure is complete and ready for submission.")
    else:
        print("⚠ Some verification checks failed.")
        print("\nPlease review the issues above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
