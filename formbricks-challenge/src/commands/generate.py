"""
Generate Command - Create realistic data using LLM

This module uses OpenAI's API to generate realistic survey structures,
user profiles, and survey responses that will be used to populate
the Formbricks instance.
"""

import json
import os
from pathlib import Path
from openai import OpenAI


class GenerateCommand:
    """Generates realistic data using Large Language Models"""
    
    def __init__(self, model="gpt-4o-mini"):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "generated"
        self.model = model
        self.client = None
        
    def execute(self):
        """Execute the data generation process"""
        print("Initiating data generation using LLM...")
        print()
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            print("Please set the environment variable and try again")
            print("Example: export OPENAI_API_KEY='your-api-key'")
            return 1
        
        self.client = OpenAI(api_key=api_key)
        
        print("Generating survey structures...")
        surveys = self._generate_surveys()
        print(f"Generated {len(surveys)} surveys")
        print()
        
        print("Generating user profiles...")
        users = self._generate_users()
        print(f"Generated {len(users)} users")
        print()
        
        print("Generating survey responses...")
        responses = self._generate_responses(surveys)
        print(f"Generated {len(responses)} responses")
        print()
        
        print("Saving generated data...")
        self._save_data("surveys.json", surveys)
        self._save_data("users.json", users)
        self._save_data("responses.json", responses)
        print()
        
        print("Data generation complete")
        print(f"Files saved to: {self.data_dir}")
        print(f"Summary: {len(surveys)} surveys, {len(users)} users, {len(responses)} responses")
        print()
        print("Next step: python main.py formbricks seed")
        
        return 0
    
    def _generate_surveys(self):
        """Generate realistic survey structures"""
        prompt = """Generate 5 diverse survey structures in JSON format. Requirements:

- Each survey should have a unique, professional name and description
- Include 3-5 questions per survey with various types
- Question types: openText, multipleChoiceSingle, multipleChoiceMulti, rating, nps
- Cover different use cases: customer feedback, employee satisfaction, product research, event feedback, user onboarding
- Use realistic question text and answer options
- Include a thank you screen for each survey

Return only a JSON array with this exact structure:
[
  {
    "name": "Survey Name",
    "description": "Survey description",
    "questions": [
      {
        "type": "openText|multipleChoiceSingle|multipleChoiceMulti|rating|nps",
        "headline": "Question text",
        "subheader": "Optional subheader",
        "required": true,
        "choices": ["Option 1", "Option 2"],
        "range": 5,
        "scale": "number"
      }
    ],
    "thankYouCard": {
      "headline": "Thank you message",
      "subheader": "Additional message"
    }
  }
]

Return only the JSON array without any markdown formatting or additional text."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        content = response.choices[0].message.content.strip()
        content = self._clean_json_response(content)
        
        return json.loads(content)
    
    def _generate_users(self):
        """Generate realistic user profiles"""
        prompt = """Generate 10 user profiles in JSON format. Requirements:

- Use realistic, diverse full names
- Create professional email addresses
- Assign roles: 5 users as "owner", 5 users as "member"

Return only a JSON array with this exact structure:
[
  {
    "name": "Full Name",
    "email": "email@domain.com",
    "role": "owner"
  }
]

Use realistic names and email addresses. Return only the JSON array without any markdown formatting."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )
        
        content = response.choices[0].message.content.strip()
        content = self._clean_json_response(content)
        
        return json.loads(content)
    
    def _generate_responses(self, surveys):
        """Generate realistic responses for surveys"""
        all_responses = []
        
        for i, survey in enumerate(surveys):
            print(f"  Processing survey {i+1}/{len(surveys)}...")
            
            questions_desc = []
            for q in survey["questions"]:
                q_type = q["type"]
                q_text = q["headline"]
                
                if q_type in ["multipleChoiceSingle", "multipleChoiceMulti"]:
                    choices = q.get("choices", [])
                    questions_desc.append(f"{q_text} (Type: {q_type}, Choices: {choices})")
                elif q_type == "rating":
                    range_val = q.get("range", 5)
                    questions_desc.append(f"{q_text} (Type: rating, Range: 1-{range_val})")
                elif q_type == "nps":
                    questions_desc.append(f"{q_text} (Type: NPS, Range: 0-10)")
                else:
                    questions_desc.append(f"{q_text} (Type: {q_type})")
            
            questions_text = "\n".join(questions_desc)
            
            prompt = f"""Generate 1 realistic survey response for this survey:

Survey: {survey['name']}

Questions:
{questions_text}

Return a JSON array with 1 response object:
[
  {{
    "surveyIndex": {i},
    "answers": {{
      "questionIndex_0": "answer value"
    }},
    "completed": true
  }}
]

Answer format:
- openText: string
- multipleChoiceSingle: string
- multipleChoiceMulti: array of strings
- rating: number
- nps: number (0-10)

Provide realistic, natural answers. Return only the JSON array without markdown formatting."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            content = self._clean_json_response(content)
            
            survey_responses = json.loads(content)
            all_responses.extend(survey_responses)
        
        return all_responses
    
    def _clean_json_response(self, content):
        """Remove markdown code blocks from LLM response"""
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return content.strip()
    
    def _save_data(self, filename, data):
        """Save data to JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
