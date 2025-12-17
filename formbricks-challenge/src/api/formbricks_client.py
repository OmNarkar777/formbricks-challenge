"""
Formbricks API Client

Provides a Python interface for interacting with Formbricks Management and Client APIs.
Handles authentication, request formatting, and response parsing.
"""

import requests
from typing import Dict, Optional


class FormbricksClient:
    """Client for Formbricks API interactions"""
    
    def __init__(self, api_key: str, base_url: str, environment_id: str, organization_id: Optional[str] = None):
        """
        Initialize the Formbricks API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of Formbricks instance
            environment_id: Environment identifier
            organization_id: Organization identifier (required for user creation)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.environment_id = environment_id
        self.organization_id = organization_id
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })
    
    def verify_connection(self) -> bool:
        """
        Verify API connectivity by calling the /me endpoint.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/management/me")
            return response.status_code == 200
        except Exception:
            return False
    
    def create_user(self, name: str, email: str, role: str = "member") -> Dict:
        """
        Create a user via Management API v2.
        Note: This endpoint is only available for self-hosted instances.
        
        Args:
            name: User's full name
            email: User's email address
            role: User's role (owner or member)
            
        Returns:
            Dict: Created user object
            
        Raises:
            ValueError: If organization_id is not set
            requests.HTTPError: If API request fails
        """
        if not self.organization_id:
            raise ValueError("organization_id is required for user creation")
        
        url = f"{self.base_url}/api/v2/organizations/{self.organization_id}/users"
        
        payload = {
            "name": name,
            "email": email,
            "role": role,
            "isActive": True
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def create_survey(self, survey_data: Dict) -> Dict:
        """
        Create a survey via Management API v1.
        
        Args:
            survey_data: Survey configuration object
            
        Returns:
            Dict: Created survey object
            
        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/api/v1/management/surveys"
        
        payload = self._transform_survey_format(survey_data)
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()["data"]
    
    def create_response(self, survey_id: str, answers: Dict, completed: bool = True) -> Dict:
        """
        Create a survey response via Client API.
        
        Args:
            survey_id: Survey identifier
            answers: Dictionary mapping question indices to answer values
            completed: Whether the response is complete
            
        Returns:
            Dict: Created response object
            
        Raises:
            requests.HTTPError: If API request fails
        """
        url = f"{self.base_url}/api/v1/client/{self.environment_id}/responses"
        
        survey = self._get_survey(survey_id)
        
        data = {}
        question_ids = [q["id"] for q in survey.get("questions", [])]
        
        for key, value in answers.items():
            if "questionIndex_" in key:
                index = int(key.split("_")[1])
                if index < len(question_ids):
                    question_id = question_ids[index]
                    data[question_id] = value
        
        payload = {
            "surveyId": survey_id,
            "finished": completed,
            "data": data
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def _get_survey(self, survey_id: str) -> Dict:
        """Retrieve survey details from Management API"""
        url = f"{self.base_url}/api/v1/management/surveys/{survey_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()["data"]
    
    def _transform_survey_format(self, survey_data: Dict) -> Dict:
        """
        Transform simplified survey structure to Formbricks API format.
        
        Args:
            survey_data: Simplified survey structure
            
        Returns:
            Dict: Formbricks-formatted survey object
        """
        questions = []
        
        for q in survey_data.get("questions", []):
            question = {
                "type": q["type"],
                "headline": {"default": q["headline"]},
                "required": q.get("required", True)
            }
            
            if q.get("subheader"):
                question["subheader"] = {"default": q["subheader"]}
            
            if q["type"] == "openText":
                question["inputType"] = "text"
                question["placeholder"] = {"default": "Type your answer here..."}
            
            elif q["type"] in ["multipleChoiceSingle", "multipleChoiceMulti"]:
                question["choices"] = [
                    {"label": {"default": choice}}
                    for choice in q.get("choices", [])
                ]
                if q["type"] == "multipleChoiceMulti":
                    question["allowMultipleSelection"] = True
            
            elif q["type"] == "rating":
                question["range"] = q.get("range", 5)
                question["scale"] = q.get("scale", "number")
                question["lowerLabel"] = {"default": "Not likely"}
                question["upperLabel"] = {"default": "Very likely"}
            
            elif q["type"] == "nps":
                question["lowerLabel"] = {"default": "Not at all likely"}
                question["upperLabel"] = {"default": "Extremely likely"}
            
            questions.append(question)
        
        thank_you = survey_data.get("thankYouCard", {})
        endings = [{
            "type": "endScreen",
            "headline": {"default": thank_you.get("headline", "Thank you!")},
            "subheader": {"default": thank_you.get("subheader", "We appreciate your feedback.")}
        }]
        
        payload = {
            "name": survey_data["name"],
            "type": "link",
            "status": "inProgress",
            "questions": questions,
            "endings": endings,
            "environmentId": self.environment_id
        }
        
        return payload
