# Setup Guide

## Prerequisites

Before beginning, ensure you have the following installed:

- Python 3.8 or higher
- Docker Engine 20.10 or higher
- Docker Compose
- Git (optional, for version control)
- curl (for downloading docker-compose.yml)

## Verification Steps

Verify installations:

```bash
python3 --version
docker --version
docker compose version
curl --version
```

All commands should return version information without errors.

## Installation Process

### Step 1: Extract Project Files

Extract the provided archive to your desired location:

```bash
tar -xzf formbricks-challenge.tar.gz
cd formbricks-challenge
```

### Step 2: Install Python Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Or use pip3 if that is your Python 3 pip:

```bash
pip3 install -r requirements.txt
```

### Step 3: Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

For persistent configuration, add to your shell profile:

```bash
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Start Formbricks

Execute the up command:

```bash
python main.py formbricks up
```

Wait for the process to complete. You should see:
- docker-compose.yml download (first run only)
- Secret generation confirmation
- Container startup logs
- Service availability confirmation

### Step 5: Complete Formbricks Setup

1. Open your browser and navigate to: http://localhost:3000

2. Complete the setup wizard:
   - Enter your name
   - Provide email address
   - Set password
   - Complete onboarding steps

3. Create API credentials:
   - Click your profile (bottom left corner)
   - Navigate to Settings
   - Select "API Keys" section
   - Click "Add API Key"
   - Choose "Production" environment
   - Copy the generated key immediately

4. Obtain environment identifier:
   - Look at your browser URL while in Formbricks
   - URL format: /environments/{environment_id}/...
   - Copy the value between /environments/ and the next /

5. Obtain organization identifier:
   - Method 1: Navigate to Settings > Organization
   - Method 2: Use browser developer tools
     - Open DevTools (F12)
     - Go to Network tab
     - Make any action in Settings
     - Inspect API requests for organizationId field

### Step 6: Create Configuration File

Create the API configuration file:

```bash
cat > data/config/api_config.json << 'EOF'
{
  "api_key": "your-actual-api-key-from-step-5",
  "base_url": "http://localhost:3000",
  "environment_id": "your-environment-id-from-step-5",
  "organization_id": "your-organization-id-from-step-5"
}
EOF
```

Replace the placeholder values with your actual values from step 5.

### Step 7: Generate Data

Execute the generate command:

```bash
python main.py formbricks generate
```

This process will:
- Connect to OpenAI API
- Generate 5 survey structures
- Generate 10 user profiles
- Generate survey responses
- Save data to data/generated/ directory

Expected duration: 30-60 seconds

### Step 8: Seed Database

Execute the seed command:

```bash
python main.py formbricks seed
```

This process will:
- Verify API connectivity
- Create 10 users via Management API
- Create 5 surveys via Management API
- Submit responses via Client API

Expected duration: 30-60 seconds

### Step 9: Verify Installation

1. Return to your browser at http://localhost:3000

2. Verify users:
   - Navigate to Settings > Organization > Members
   - Confirm 10 new users are listed
   - Verify role distribution (5 owners, 5 members)

3. Verify surveys:
   - Go to Surveys section
   - Confirm 5 surveys are listed
   - Open each survey to view questions

4. Verify responses:
   - Click on any survey
   - Navigate to Responses tab
   - Confirm at least 1 response exists
   - View response details

## Troubleshooting Setup Issues

### Python Dependencies Fail to Install

If pip install fails:

```bash
# Try upgrading pip first
pip install --upgrade pip

# Or use pip3 explicitly
pip3 install -r requirements.txt

# Or create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker Containers Fail to Start

Check for port conflicts:

```bash
# Check if port 3000 is in use
lsof -i :3000

# Check if port 5432 is in use
lsof -i :5432

# If ports are in use, stop conflicting services
```

Verify Docker is running:

```bash
docker ps

# If error, start Docker daemon
sudo systemctl start docker
```

Check Docker logs:

```bash
docker compose -f docker/docker-compose.yml logs
```

### OpenAI API Connection Fails

Verify API key:

```bash
# Test with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Check for:
- Correct API key format
- Valid API key (not expired)
- Sufficient quota
- Network connectivity

### Formbricks API Connection Fails

Verify configuration:

```bash
# Check file exists
cat data/config/api_config.json

# Test API endpoint
curl -H "x-api-key: YOUR_API_KEY" \
  http://localhost:3000/api/v1/management/me
```

Common issues:
- Incorrect API key
- Wrong environment_id
- Wrong organization_id
- Formbricks not running

### User Creation Fails

Note: User creation via API only works on self-hosted instances.

If all users fail to create:
- Verify organization_id is correct
- Check API key has sufficient permissions
- Review Formbricks logs for errors

### Response Creation Fails

If responses fail to create:
- Verify survey IDs are correct
- Check question ID mapping
- Ensure data format matches question types
- Review data/generated/responses.json

## Post-Installation

### Stopping Formbricks

When finished:

```bash
python main.py formbricks down
```

This stops containers and removes volumes.

### Starting Again

To start fresh:

```bash
# Start Formbricks
python main.py formbricks up

# Note: You will need to complete setup wizard again
# And create new API credentials
```

### Keeping Data

To preserve data between sessions:

```bash
# Stop without removing volumes
docker compose -f docker/docker-compose.yml stop

# Start again later
docker compose -f docker/docker-compose.yml start
```

## Additional Configuration

### Using Different LLM Model

Specify model during generation:

```bash
python main.py formbricks generate --model gpt-4o
```

Available models:
- gpt-4o-mini (default, fast and economical)
- gpt-4o (more capable)
- gpt-3.5-turbo (faster, less capable)

### Customizing Data Generation

Edit prompts in src/commands/generate.py to:
- Change survey themes
- Adjust question complexity
- Modify response patterns
- Add more surveys/users/responses

## Validation

After setup, verify:

1. All Python dependencies installed
2. Docker containers running
3. Formbricks accessible at http://localhost:3000
4. API configuration file created
5. Generated data files exist
6. Surveys visible in UI
7. Users listed in Settings
8. Responses present in surveys

## Getting Help

If issues persist:

1. Review error messages carefully
2. Check logs: `docker compose -f docker/docker-compose.yml logs`
3. Verify all prerequisites are met
4. Ensure correct versions of dependencies
5. Review TECHNICAL.md for architecture details

## Next Steps

After successful setup:

1. Explore generated surveys in Formbricks UI
2. Review generated data in data/generated/ directory
3. Examine code in src/ directory
4. Read TECHNICAL.md for implementation details
5. Experiment with customizations
