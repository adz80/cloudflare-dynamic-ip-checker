# Cloudflare Dynamic DNS Updater

A Python script that automatically updates Cloudflare DNS records when your public IP address changes. It includes features like email notifications and comprehensive logging.

## Features

- Automatically detects IP address changes
- Updates Cloudflare DNS records
- Email notifications when IP changes (optional)
- Configurable check intervals
- Detailed logging
- Docker support

## Prerequisites

- Python 3.6+
- Cloudflare account with API access
- Domain managed by Cloudflare
- SMTP server details (optional, for email notifications)

## Environment Variables

### Required Variables
- `CF_ZONE_ID`: Your Cloudflare Zone ID
- `CF_BEARER_TOKEN`: Your Cloudflare API Token
- `CF_RECORD`: The domain name to update (e.g., "subdomain.example.com")

### Optional Variables
- `INTERVAL`: Check interval in hours (default: 12)
- `EMAIL`: Email address for notifications (default: "nobody@nobody.com")
- `SMTP_SERVER`: SMTP server address (default: "localhost")
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `LOG_FILE`: Log file path (default: "ipchanges.log")
- `SEND_EMAIL`: Enable email notifications (default: "False")
- `LOGGING_LEVEL`: Logging level (default: "INFO")

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cf-dyndns-updater.git
cd cf-dyndns-updater
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export CF_ZONE_ID="your_zone_id"
export CF_BEARER_TOKEN="your_api_token"
export CF_RECORD="your.domain.com"
```

4. Run the script:
```bash
python dyndns_updater.py
```

### Docker Installation

1. Build and run using Docker Compose:
```bash
docker-compose up -d
```

Or build and run manually:
```bash
docker build -t cf-dyndns-updater .
docker run -d --name cf-dyndns \
    -e CF_ZONE_ID="your_zone_id" \
    -e CF_BEARER_TOKEN="your_api_token" \
    -e CF_RECORD="your.domain.com" \
    cf-dyndns-updater
```

## Logging

The script creates a log file (default: ipchanges.log) containing all IP changes and potential errors. The logging level can be configured using the `LOGGING_LEVEL` environment variable.

Example log output:
```
2024-12-30 10:00:00 :: INFO :: IP is up to date
2024-12-30 10:00:00 :: INFO :: Sleeping for 12 hours
2024-12-30 22:00:00 :: INFO :: IP change from 192.168.1.1 to 192.168.1.2
```

## Email Notifications

To enable email notifications:

1. Set the following environment variables:
```bash
export SEND_EMAIL="True"
export EMAIL="your@email.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_username"
export SMTP_PASSWORD="your_password"
```

2. The script will send notifications whenever your IP address changes.

## Contributing

Feel free to submit issues and pull requests.

## License

MIT License - feel free to use this project as you wish.
