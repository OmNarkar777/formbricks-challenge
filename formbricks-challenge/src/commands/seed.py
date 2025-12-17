"""
Seed Command - Populate Formbricks using APIs

This module reads generated data files and uses Formbricks Management
and Client APIs to populate the instance with surveys, users, and responses.
No direct database manipulation is performed.
"""

import json
import time
from pathlib import Path
from api.formbricks_client import FormbricksClient


class SeedCommand:
    """Populates Formbricks using API calls only"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "generated"
        self.config_dir = self.project_root / "data" / "config"
        self.client = None
        
    def execute(self):
        """Execute the seeding process"""
        print("Initiating Formbricks seeding process...")
        print()
        
        config_file = self.config_dir / "api_config.json"
        if not config_file.exists():
            print("Error: Configuration file not found")
            print(f"Expected location: {config_file}")
            print()
            print("Required configuration format:")
            print('{')
            print('  "api_key": "your-api-key",')
            print('  "base_url": "http://localhost:3000",')
            print('  "environment_id": "your-environment-id",')
            print('  "organization_id": "your-organization-id"')
            print('}')
            print()
            print("Obtain these values from Formbricks UI after setup")
            return 1
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.client = FormbricksClient(
            api_key=config["api_key"],
            base_url=config["base_url"],
            environment_id=config["environment_id"],
            organization_id=config.get("organization_id")
        )
        
        print("Verifying API connection...")
        if not self.client.verify_connection():
            print("Error: Failed to connect to Formbricks API")
            print("Please verify your configuration and ensure Formbricks is running")
            return 1
        print("Connection verified successfully")
        print()
        
        surveys_data = self._load_data("surveys.json")
        users_data = self._load_data("users.json")
        responses_data = self._load_data("responses.json")
        
        print("Creating users...")
        created_users = self._seed_users(users_data)
        
        print()
        print("Creating surveys...")
        created_surveys = self._seed_surveys(surveys_data)
        
        print()
        print("Creating survey responses...")
        created_responses = self._seed_responses(responses_data, created_surveys)
        
        print()
        print("=" * 60)
        print("Seeding process complete")
        print("=" * 60)
        print(f"Users created: {len(created_users)}")
        print(f"Surveys created: {len(created_surveys)}")
        print(f"Responses created: {len(created_responses)}")
        print()
        print("Access your populated instance at: http://localhost:3000")
        
        return 0
    
    def _load_data(self, filename):
        """Load data from JSON file"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Required file not found: {filename}. Run 'generate' command first.")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _seed_users(self, users_data):
        """Create users via Management API"""
        created = []
        
        for i, user in enumerate(users_data, 1):
            print(f"  [{i}/{len(users_data)}] Creating user: {user['name']}")
            
            try:
                result = self.client.create_user(
                    name=user["name"],
                    email=user["email"],
                    role=user["role"]
                )
                created.append(result)
                print(f"      Success - Role: {user['role']}")
            except Exception as e:
                print(f"      Failed: {str(e)}")
            
            time.sleep(0.5)
        
        return created
    
    def _seed_surveys(self, surveys_data):
        """Create surveys via Management API"""
        created = []
        
        for i, survey in enumerate(surveys_data, 1):
            print(f"  [{i}/{len(surveys_data)}] Creating survey: {survey['name']}")
            
            try:
                result = self.client.create_survey(survey)
                created.append(result)
                print(f"      Success - Questions: {len(survey['questions'])}")
            except Exception as e:
                print(f"      Failed: {str(e)}")
            
            time.sleep(0.5)
        
        return created
    
    def _seed_responses(self, responses_data, created_surveys):
        """Create survey responses via Client API"""
        created = []
        
        for i, response in enumerate(responses_data, 1):
            survey_index = response.get("surveyIndex", 0)
            
            if survey_index >= len(created_surveys):
                print(f"  [{i}] Skipped - Invalid survey index")
                continue
            
            survey = created_surveys[survey_index]
            survey_id = survey.get("id")
            
            print(f"  [{i}/{len(responses_data)}] Creating response for survey {survey_index + 1}")
            
            try:
                result = self.client.create_response(
                    survey_id=survey_id,
                    answers=response["answers"],
                    completed=response.get("completed", True)
                )
                created.append(result)
                print(f"      Success")
            except Exception as e:
                print(f"      Failed: {str(e)}")
            
            time.sleep(0.5)
        
        return created
