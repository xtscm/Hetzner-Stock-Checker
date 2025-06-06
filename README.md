# Hetzner cx32 Server Availability Monitor

A Python script that continuously monitors Hetzner Cloud for cx32 server availability across multiple datacenters and sends real-time macOS notifications when servers become available.

## Features

- **Real-time monitoring** of cx32 server availability across multiple Hetzner datacenters
- **macOS notifications** when servers become available or unavailable
- **Configurable check intervals** (default: 5 seconds)
- **Multiple datacenter support** (Helsinki, Falkenstein, Nuremberg)
- **Detailed logging** with timestamp tracking
- **Error handling** and recovery
- **Initial connectivity test** using cpx21 servers

## Supported Datacenters

The monitor checks the following Hetzner datacenters:
- `hel1-dc2` (Helsinki, Finland)
- `fsn1-dc14` (Falkenstein, Germany) 
- `nbg1-dc3` (Nuremberg, Germany)

## Requirements

- Python 3.6+
- macOS (for notifications)
- Hetzner Cloud API token
- Internet connection

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/xtscm/hetzner-stock-checker.git
   cd hetzner-stock-checker
   ```

2. **Install required packages:**
   ```bash
   pip install requests python-dotenv
   ```

3. **Create environment file:**
   ```bash
   touch .env
   ```

4. **Add your Hetzner API token to `.env`:**
   ```
   HETZNER_TOKEN=your_hetzner_api_token_here
   ```

## Getting a Hetzner API Token

1. Log in to your [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Go to your project
3. Navigate to **Security** → **API Tokens**
4. Click **Generate API Token**
5. Give it a name (e.g., "Server Monitor") and select **Read** permissions
6. Copy the token and add it to your `.env` file

## Usage

### Basic Usage

Run the monitor with default settings:
```bash
python3 hetzner_monitor.py
```

### Configuration

You can modify the following variables in the script:

```python
CHECK_INTERVAL = 5  # seconds between checks
SERVER_TYPE = 'cx32'  # server type to monitor
DATACENTER_NAMES = ['hel1-dc2', 'fsn1-dc14', 'nbg1-dc3']  # datacenters to check
```

### Running in Background

To run the monitor continuously in the background:
```bash
nohup python3 hetzner_monitor.py > monitor.log 2>&1 &
```

To stop the background process:
```bash
pkill -f hetzner_monitor.py
```

## Output Examples

### When servers become available:
```
[2025-06-06 10:30:15.123456] cx32 available in hel1-dc2 (Helsinki)
[2025-06-06 10:30:15.123456] cx32 available in: hel1-dc2
```

### When no servers are available:
```
[2025-06-06 10:30:20.123456] cx32 not available in any datacenter
```

### Initial test output:
```
[INIT TEST] cpx21 is available in HEL1
Monitoring cx32 (ID: 3)
```

## Notifications

The script sends macOS notifications for:
- ✅ **Server availability**: When cx32 becomes available in a datacenter
- ❌ **Errors**: API failures or connection issues
- 🔄 **Status updates**: Monitor start/stop events

## Troubleshooting

### Common Issues

**1. "HETZNER_TOKEN not found in environment"**
- Ensure your `.env` file exists and contains `HETZNER_TOKEN=your_token`
- Check that the token has proper read permissions

**2. "Could not find cx32 server type"**
- Verify your API token is valid
- Check internet connectivity
- Ensure the token has project access

**3. API rate limiting**
- The default 5-second interval should be safe
- If you encounter rate limits, increase `CHECK_INTERVAL`

**4. No notifications appearing**
- Ensure you're running on macOS
- Check macOS notification settings
- Verify the script has permission to send notifications

### Debug Mode

For detailed HTTP request logging, the script enables debug logging by default. Check the console output for detailed API interaction logs.

### Checking Logs

When running in background mode, check the log file:
```bash
tail -f monitor.log
```

## API Reference

The script uses the following Hetzner Cloud API endpoints:
- `GET /v1/server_types` - Fetch available server types
- `GET /v1/datacenters` - List all datacenters
- `GET /v1/datacenters/{id}` - Get datacenter details and availability
