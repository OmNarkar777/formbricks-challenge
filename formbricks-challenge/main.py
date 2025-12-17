#!/usr/bin/env python3
"""
Formbricks Challenge - Main Entry Point

This script provides command-line interface for managing Formbricks operations.
Available commands:
  - up: Start Formbricks locally using Docker Compose
  - down: Stop and clean up Formbricks containers
  - generate: Generate realistic data using LLM
  - seed: Populate Formbricks using APIs
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from commands.up import UpCommand
from commands.down import DownCommand
from commands.generate import GenerateCommand
from commands.seed import SeedCommand


def main():
    parser = argparse.ArgumentParser(
        description="Formbricks Challenge - API-driven data management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    up_parser = subparsers.add_parser("up", help="Start Formbricks locally")
    up_parser.add_argument("app", choices=["formbricks"])
    
    down_parser = subparsers.add_parser("down", help="Stop Formbricks")
    down_parser.add_argument("app", choices=["formbricks"])
    
    gen_parser = subparsers.add_parser("generate", help="Generate realistic data")
    gen_parser.add_argument("app", choices=["formbricks"])
    gen_parser.add_argument("--model", default="gpt-4o-mini", help="LLM model")
    
    seed_parser = subparsers.add_parser("seed", help="Seed Formbricks with data")
    seed_parser.add_argument("app", choices=["formbricks"])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "up":
            cmd = UpCommand()
            return cmd.execute()
        elif args.command == "down":
            cmd = DownCommand()
            return cmd.execute()
        elif args.command == "generate":
            cmd = GenerateCommand(model=args.model)
            return cmd.execute()
        elif args.command == "seed":
            cmd = SeedCommand()
            return cmd.execute()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
