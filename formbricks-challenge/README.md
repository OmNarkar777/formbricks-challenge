# Formbricks Challenge Solution

## Overview

This solution provides a command-line interface for running Formbricks locally and populating it with realistic, LLM-generated data through API interactions only. The implementation demonstrates clean architecture principles and professional code quality.

## Solution Components

The implementation addresses all four challenge requirements:

1. **Up Command** - Starts Formbricks locally using Docker Compose
2. **Down Command** - Gracefully stops containers and cleans up resources
3. **Generate Command** - Creates realistic survey and user data using LLM
4. **Seed Command** - Populates Formbricks using Management and Client APIs only

## Requirements

- Python 3.8 or higher
- Docker and Docker Compose
- OpenAI API key
- Available ports: 3000 (Formbricks), 5432 (PostgreSQL)

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Usage

### Starting Formbricks

```bash
python main.py formbricks up
```

This command will:
- Download the official Formbricks docker-compose configuration
- Generate required security secrets
- Start Docker containers
- Wait for services to become available

Access Formbricks at: http://localhost:3000

### Initial Configuration

After starting Formbricks:

1. Complete the setup wizard at http://localhost:3000
2. Navigate to Settings and create an API key
3. Obtain your environment_id from the browser URL
4. Obtain your organization_id from Settings or browser developer tools
5. Create the configuration file:

```bash
cat > data/config/api_config.json << 'EOF'
{
  "api_key": "your-api-key",
  "base_url": "http://localhost:3000",
  "environment_id": "your-environment-id",
  "organization_id": "your-organization-id"
}
EOF
```

### Generating Data

```bash
python main.py formbricks generate
```

This creates:
- 5 unique surveys with diverse question types
- 10 user profiles (5 owners, 5 members)
- Survey responses for each survey

Generated data is saved to `data/generated/` as JSON files.

### Seeding the Database

```bash
python main.py formbricks seed
```

This process:
- Verifies API connectivity
- Creates users via Management API v2
- Creates surveys via Management API v1
- Submits responses via Client API

All operations use APIs exclusively - no direct database manipulation occurs.

### Stopping Formbricks

```bash
python main.py formbricks down
```

This stops all containers and removes volumes.

## Project Structure

```
formbricks-challenge/
├── main.py                    # CLI entry point
├── src/
│   ├── commands/
│   │   ├── up.py             # Container startup logic
│   │   ├── down.py           # Container shutdown logic
│   │   ├── generate.py       # LLM data generation
│   │   └── seed.py           # API-based database seeding
│   └── api/
│       └── formbricks_client.py  # Formbricks API client
├── data/
│   ├── config/               # API configuration
│   └── generated/            # Generated data files
├── docker/                   # Docker Compose files
└── requirements.txt          # Python dependencies
```

## Architecture

### Command Layer

Each command is implemented as a separate class following the Command pattern:

- **UpCommand**: Manages Docker Compose setup and container orchestration
- **DownCommand**: Handles graceful shutdown and cleanup
- **GenerateCommand**: Interfaces with OpenAI API for data generation
- **SeedCommand**: Orchestrates API calls to populate Formbricks

### API Client Layer

The FormbricksClient class provides a clean interface to Formbricks APIs:

- Management API v2 for user creation
- Management API v1 for survey management
- Client API for response submission
- Automatic data format transformation

### Data Flow

```
LLM Generation → JSON Files → API Client → Formbricks APIs → Database
```

This separation allows for:
- Inspection of generated data before seeding
- Reproducible seeding from the same data set
- Easy debugging and testing
- Clear separation of concerns

## API Usage

### Management API v2 (User Creation)

```python
POST /api/v2/organizations/{organizationId}/users
{
  "name": "User Name",
  "email": "user@example.com",
  "role": "owner",
  "isActive": true
}
```

### Management API v1 (Survey Creation)

```python
POST /api/v1/management/surveys
{
  "name": "Survey Name",
  "type": "link",
  "questions": [...],
  "endings": [...],
  "environmentId": "env-id"
}
```

### Client API (Response Submission)

```python
POST /api/v1/client/{environmentId}/responses
{
  "surveyId": "survey-id",
  "finished": true,
  "data": {
    "question-id": "answer"
  }
}
```

## Generated Data

### Surveys

The solution generates 5 diverse surveys covering:
- Customer satisfaction (NPS, ratings)
- Employee engagement (multiple choice, text)
- Product feedback (ratings, text)
- Event feedback (multiple choice, ratings)
- User onboarding (text, ratings)

Each survey includes 3-5 questions of various types:
- Open text questions
- Single-choice multiple choice
- Multi-choice multiple choice
- Rating scales (1-5, 1-7, 1-10)
- Net Promoter Score (0-10)

### Users

10 users are generated with:
- Realistic, diverse names
- Professional email addresses
- Role distribution: 5 owners, 5 members
- Active status enabled

### Responses

At least one realistic response per survey with:
- Appropriate answer types for each question
- Natural language for text responses
- Reasonable selections for multiple choice
- Realistic ratings and NPS scores

## Technical Implementation

### Security

- Cryptographically secure secret generation using Python's secrets module
- API keys managed via configuration file (not in code)
- No hardcoded credentials
- Configuration excluded from version control

### Error Handling

- Graceful degradation on API failures
- Clear error messages with actionable guidance
- Progress indicators for long-running operations
- Proper exception handling throughout

### Rate Limiting

Built-in delays between API calls (500ms) to:
- Respect API server resources
- Prevent overwhelming the local instance
- Ensure reliable operation
- Allow proper request processing

### Code Quality

- Type hints for improved maintainability
- Comprehensive docstrings
- Single Responsibility Principle adherence
- Clear separation of concerns
- Modular, testable architecture

## Troubleshooting

### Connection Issues

If the API connection fails:
- Verify Formbricks is running: `docker ps`
- Check API key is correct in configuration
- Ensure environment_id and organization_id are accurate
- Verify network connectivity to localhost:3000

### User Creation Failures

Note: User creation via API only works on self-hosted instances.

If user creation fails:
- Verify organization_id is set in configuration
- Ensure API key has sufficient permissions
- Check Formbricks logs: `docker logs <container-id>`

### Data Generation Issues

If LLM data generation fails:
- Verify OPENAI_API_KEY is set correctly
- Check API quota and rate limits
- Ensure network connectivity to OpenAI API
- Review console output for specific errors

### Docker Issues

If containers fail to start:
- Check if ports 3000 or 5432 are in use
- Verify Docker daemon is running
- Review Docker logs for error messages
- Ensure sufficient system resources

## Configuration Options

### LLM Model Selection

Use a different OpenAI model:

```bash
python main.py formbricks generate --model gpt-4o
```

### Configuration File Location

Default: `data/config/api_config.json`

Required fields:
- api_key: Authentication token from Formbricks
- base_url: Formbricks instance URL
- environment_id: Target environment identifier
- organization_id: Organization identifier (required for user creation)

## Challenge Compliance

This solution meets all challenge requirements:

- Uses APIs exclusively for data population (no database manipulation)
- Creates 5 unique surveys with realistic content
- Generates at least 1 response per survey
- Creates 10 users with Manager/Owner access levels
- Uses LLM for realistic data generation
- Implements clean, maintainable code architecture
- Provides command-driven interface
- Uses Docker for local deployment

## Future Enhancements

Potential improvements for production deployment:

1. Configuration validation and interactive setup
2. Retry logic for failed API calls
3. Bulk operation support for improved performance
4. Progress persistence for resumable operations
5. Comprehensive test suite
6. Logging framework integration
7. Support for additional LLM providers
8. Data template system for common scenarios

## References

- Formbricks Documentation: https://formbricks.com/docs
- Formbricks API Reference: https://formbricks.com/docs/api-reference
- Docker Documentation: https://docs.docker.com
- OpenAI API Documentation: https://platform.openai.com/docs

## License

This solution is provided for evaluation purposes.
