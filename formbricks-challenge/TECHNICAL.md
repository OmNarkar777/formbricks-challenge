# Technical Documentation

## Architecture Overview

This solution implements a clean, modular architecture for managing Formbricks operations through a command-line interface. The design follows established software engineering principles to ensure maintainability, testability, and extensibility.

## Design Principles

### Command Pattern

Each operation (up, down, generate, seed) is encapsulated in its own command class. This provides:

- Clear separation of concerns
- Single Responsibility Principle compliance
- Easy unit testing capability
- Simple extensibility for new commands

### API Abstraction Layer

The FormbricksClient class abstracts all API interactions, providing:

- Centralized authentication handling
- Request/response format transformation
- Type-safe method signatures
- Error handling consistency

### Data Pipeline

The system implements a clear data flow:

```
Data Generation → JSON Storage → API Consumption → Database Population
```

This separation provides several advantages:

1. Data can be inspected before seeding
2. Same data can be used for multiple runs
3. Generation and seeding are independent
4. Easy debugging and validation

## Component Details

### CLI Layer (main.py)

The entry point uses Python's argparse for command parsing. It provides:

- Consistent command structure
- Built-in help documentation
- Argument validation
- Error handling at the top level

### Command Layer (src/commands/)

#### UpCommand

Responsibilities:
- Download official docker-compose configuration
- Generate cryptographically secure secrets
- Start Docker containers
- Wait for service availability

Implementation notes:
- Uses subprocess for Docker interactions
- Implements polling for service readiness
- Generates 256-bit secrets using secrets.token_hex()

#### DownCommand

Responsibilities:
- Stop Docker containers gracefully
- Remove volumes to ensure clean state
- Provide feedback on cleanup status

Implementation notes:
- Uses docker-compose down -v for complete cleanup
- Handles missing compose file gracefully

#### GenerateCommand

Responsibilities:
- Interface with OpenAI API
- Generate survey structures
- Generate user profiles
- Generate survey responses
- Save data to JSON files

Implementation notes:
- Uses structured prompts for consistent output
- Parses and cleans LLM responses
- Handles markdown code blocks
- Creates realistic, diverse data

#### SeedCommand

Responsibilities:
- Load configuration and generated data
- Verify API connectivity
- Create users via Management API
- Create surveys via Management API
- Submit responses via Client API
- Provide progress feedback

Implementation notes:
- Implements rate limiting (500ms delays)
- Continues on individual failures
- Maps question indices to IDs for responses

### API Layer (src/api/formbricks_client.py)

The API client provides methods for:

1. Connection verification
2. User creation (Management API v2)
3. Survey creation (Management API v1)
4. Response submission (Client API)

Key features:
- Session-based request handling
- Automatic authentication headers
- Data format transformation
- Type hints for all methods

## API Integration

### Management API v2

Used for user creation. Endpoint:

```
POST /api/v2/organizations/{organizationId}/users
```

Note: Only available on self-hosted instances.

### Management API v1

Used for survey management. Endpoint:

```
POST /api/v1/management/surveys
```

Requires transformation from simplified format to Formbricks structure.

### Client API

Used for response submission. Endpoint:

```
POST /api/v1/client/{environmentId}/responses
```

Does not require authentication.

## Data Formats

### Generated Survey Format

Simplified structure for ease of generation:

```json
{
  "name": "Survey Name",
  "description": "Description",
  "questions": [
    {
      "type": "openText",
      "headline": "Question text",
      "required": true
    }
  ],
  "thankYouCard": {
    "headline": "Thank you",
    "subheader": "Message"
  }
}
```

### Formbricks API Format

Extended structure required by API:

```json
{
  "name": "Survey Name",
  "type": "link",
  "status": "inProgress",
  "questions": [
    {
      "type": "openText",
      "headline": {"default": "Question text"},
      "inputType": "text",
      "placeholder": {"default": "Type here..."},
      "required": true
    }
  ],
  "endings": [{
    "type": "endScreen",
    "headline": {"default": "Thank you"},
    "subheader": {"default": "Message"}
  }],
  "environmentId": "env-id"
}
```

The transformation is handled by `_transform_survey_format()` method.

## Error Handling Strategy

### Graceful Degradation

The seed command continues processing even if individual operations fail. This ensures partial success is useful and provides clear feedback on what succeeded and what failed.

### User-Friendly Messages

All error messages include:
- Clear description of the problem
- Actionable guidance for resolution
- Context about what was being attempted

### Exception Hierarchy

```
KeyboardInterrupt → Handled at main() level
API Errors → Handled at command level
Configuration Errors → Caught early with clear messages
```

## Security Considerations

### Secret Generation

Uses Python's secrets module for cryptographically secure random generation:

```python
secrets.token_hex(32)  # 256-bit key
```

This is appropriate for:
- NEXTAUTH_SECRET
- ENCRYPTION_KEY
- CRON_SECRET

### API Key Management

- Stored in configuration file
- Never hardcoded in source
- Excluded from version control
- User-managed, not generated

### Docker Security

- Only necessary ports exposed (3000)
- PostgreSQL not accessible externally
- Volumes used for data persistence
- Clean shutdown with volume removal

## Performance Characteristics

### Rate Limiting

Implements 500ms delays between API calls to:
- Prevent server overload
- Ensure reliable processing
- Allow proper database operations
- Respect API server resources

Trade-off: Slower seeding in exchange for reliability.

### LLM Calls

Generation makes multiple API calls:
- 1 call for surveys
- 1 call for users
- 5 calls for responses (1 per survey)

Total: Approximately 7 API calls to OpenAI.

### Docker Operations

Container startup time depends on:
- Image download (first run only)
- Service initialization
- Database migration

Typical time: 30-60 seconds.

## Testing Considerations

### Manual Testing

The system is designed for easy manual testing with:
- Clear progress indicators
- Verbose error messages
- Step-by-step workflow
- Inspection points (generated JSON files)

### Automated Testing

The architecture supports automated testing:

```python
# Example unit test structure
class TestGenerateCommand(unittest.TestCase):
    def setUp(self):
        self.cmd = GenerateCommand(model="gpt-4o-mini")
        # Mock OpenAI client
        
    def test_survey_generation(self):
        # Test survey structure
        pass
```

Mocking points:
- OpenAI API client
- Formbricks API client
- Docker subprocess calls

## Extensibility

### Adding New Commands

Create new command class:

```python
# src/commands/backup.py
class BackupCommand:
    def execute(self):
        # Implementation
        pass
```

Register in main.py:

```python
backup_parser = subparsers.add_parser("backup")
# Handle in main()
```

### Adding New API Methods

Extend FormbricksClient:

```python
def delete_survey(self, survey_id: str) -> bool:
    url = f"{self.base_url}/api/v1/management/surveys/{survey_id}"
    response = self.session.delete(url)
    response.raise_for_status()
    return True
```

### Configuration Options

Add new fields to api_config.json:

```json
{
  "api_key": "...",
  "base_url": "...",
  "timeout": 30,
  "retry_attempts": 3
}
```

Update FormbricksClient constructor to accept new parameters.

## Deployment Considerations

### Production Deployment

For production use, consider:

1. Environment variable management
2. Secrets management system
3. Logging framework
4. Monitoring integration
5. Error alerting
6. Backup procedures

### Scaling

Current design handles:
- Single instance deployment
- Small to medium data volumes
- Sequential API operations

For larger scale:
- Implement parallel API calls
- Use bulk API endpoints (if available)
- Consider database direct access for large volumes

## Dependencies

### Python Packages

- requests: HTTP client for API calls
- openai: Official OpenAI SDK

### External Services

- Docker: Container runtime
- Docker Compose: Container orchestration
- OpenAI API: LLM for data generation
- Formbricks: Target application

### System Requirements

- Python 3.8+
- Docker 20.10+
- 2GB RAM minimum
- 5GB disk space

## Troubleshooting Guide

### Common Issues

1. Port conflicts: Check with `netstat -an | grep 3000`
2. Docker not running: Verify with `docker ps`
3. API key issues: Test with curl to /api/v1/management/me
4. Network issues: Check firewall and proxy settings

### Debug Mode

Enable verbose output:

```bash
# For Docker operations
docker compose -f docker/docker-compose.yml logs -f

# For API calls
# Add print statements in formbricks_client.py
```

### Log Files

Check Docker logs:

```bash
docker logs formbricks-formbricks-1
docker logs formbricks-postgres-1
```

## Known Limitations

1. User creation only works on self-hosted instances
2. Sequential API operations (no parallel processing)
3. No retry logic for failed API calls
4. No progress persistence for interrupted operations
5. Limited to OpenAI for LLM (no alternative providers)

## Future Improvements

Potential enhancements:

1. Add retry logic with exponential backoff
2. Implement bulk operations support
3. Add validation before seeding
4. Create dry-run mode
5. Add comprehensive logging
6. Support alternative LLM providers
7. Implement progress persistence
8. Add configuration validation
9. Create interactive setup wizard
10. Add comprehensive test suite

## References

- Formbricks API Documentation: https://formbricks.com/docs/api-reference
- Docker Compose Specification: https://docs.docker.com/compose/
- Python Requests Library: https://requests.readthedocs.io/
- OpenAI API Documentation: https://platform.openai.com/docs
