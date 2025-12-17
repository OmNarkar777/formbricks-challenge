"""
Down Command - Stop and clean up Formbricks containers

This module handles graceful shutdown of Formbricks services
and cleanup of Docker containers and volumes.
"""

import subprocess
from pathlib import Path


class DownCommand:
    """Manages Formbricks shutdown and cleanup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.docker_dir = self.project_root / "docker"
        self.compose_file = self.docker_dir / "docker-compose.yml"
        
    def execute(self):
        """Execute the shutdown sequence"""
        print("Stopping Formbricks services...")
        print()
        
        if not self.compose_file.exists():
            print("Error: docker-compose.yml not found")
            print("No services to stop")
            return 1
        
        print("Stopping and removing containers...")
        result = subprocess.run(
            ["docker", "compose", "-f", str(self.compose_file), "down", "-v"],
            cwd=self.docker_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Warning: {result.stderr}")
        else:
            if result.stdout:
                print(result.stdout)
        
        print("Formbricks has been stopped")
        print("All containers and volumes have been removed")
        print("Note: Run 'up' command to start fresh")
        
        return 0
