"""
Up Command - Start Formbricks locally using Docker Compose

This module handles the initialization and startup of Formbricks,
including downloading the docker-compose configuration, generating
required security secrets, and starting the containers.
"""

import subprocess
import secrets
import time
from pathlib import Path


class UpCommand:
    """Manages Formbricks startup using Docker Compose"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.docker_dir = self.project_root / "docker"
        self.compose_file = self.docker_dir / "docker-compose.yml"
        
    def execute(self):
        """Execute the startup sequence"""
        print("Starting Formbricks setup...")
        print()
        
        self.docker_dir.mkdir(exist_ok=True)
        
        if not self.compose_file.exists():
            print("Downloading docker-compose.yml from Formbricks repository...")
            self._download_compose_file()
            print("Download complete")
            print()
        
        print("Generating security secrets...")
        self._generate_secrets()
        print("Secrets generated successfully")
        print()
        
        print("Starting Docker containers...")
        self._start_docker()
        print()
        
        print("Waiting for services to be ready...")
        self._wait_for_service()
        print()
        
        print("Formbricks is now running")
        print("Access URL: http://localhost:3000")
        print()
        print("Next steps:")
        print("1. Visit http://localhost:3000 and complete the setup wizard")
        print("2. Create an API key in Settings")
        print("3. Save configuration to data/config/api_config.json")
        print("4. Run: python main.py formbricks generate")
        
        return 0
    
    def _download_compose_file(self):
        """Download the official docker-compose.yml file"""
        url = "https://raw.githubusercontent.com/formbricks/formbricks/stable/docker/docker-compose.yml"
        
        result = subprocess.run(
            ["curl", "-fsSL", "-o", str(self.compose_file), url],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to download docker-compose.yml: {result.stderr}")
    
    def _generate_secrets(self):
        """Generate cryptographically secure secrets"""
        nextauth_secret = secrets.token_hex(32)
        encryption_key = secrets.token_hex(32)
        cron_secret = secrets.token_hex(32)
        
        with open(self.compose_file, 'r') as f:
            content = f.read()
        
        content = content.replace('NEXTAUTH_SECRET:', f'NEXTAUTH_SECRET: {nextauth_secret}')
        content = content.replace('ENCRYPTION_KEY:', f'ENCRYPTION_KEY: {encryption_key}')
        content = content.replace('CRON_SECRET:', f'CRON_SECRET: {cron_secret}')
        
        with open(self.compose_file, 'w') as f:
            f.write(content)
    
    def _start_docker(self):
        """Start Docker Compose services"""
        result = subprocess.run(
            ["docker", "compose", "-f", str(self.compose_file), "up", "-d"],
            cwd=self.docker_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to start Docker services: {result.stderr}")
        
        if result.stdout:
            print(result.stdout)
    
    def _wait_for_service(self, max_attempts=30):
        """Wait for Formbricks service to become available"""
        for i in range(max_attempts):
            try:
                result = subprocess.run(
                    ["curl", "-f", "http://localhost:3000/api/health"],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return
            except:
                pass
            
            time.sleep(2)
            if (i + 1) % 5 == 0:
                print(f"Still waiting... (attempt {i+1}/{max_attempts})")
        
        print("Note: Service may still be initializing. Check with: docker ps")
