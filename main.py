#!/usr/bin/env python3
"""
Hetzner cx32 Server Availability Monitor
Checks for cx32 server availability and sends macOS notifications
"""

import os
import requests
import time
import subprocess
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable debug logging for HTTP requests
logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

# Configuration
API_TOKEN = os.getenv('HETZNER_TOKEN')
CHECK_INTERVAL = 5  # seconds between checks
SERVER_TYPE = 'cx32'
TEST_SERVER_TYPE = 'cpx21'
TEST_DATACENTER_NAME = 'hel1-dc2'

# Known datacenter names for cx32
DATACENTER_NAMES = ['hel1-dc2', 'fsn1-dc14', 'nbg1-dc3']

def send_notification(title, message):
    """Send a macOS notification"""
    cmd = f'''
    osascript -e 'display notification "{message}" with title "{title}" sound name "default"'
    '''
    subprocess.run(cmd, shell=True)

def get_server_type_id(name):
    """Get the ID for a server type by name"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }

    print(f"[DEBUG] Fetching server types for {name}...")
    response = requests.get(
        'https://api.hetzner.cloud/v1/server_types',
        headers=headers
    )
    print(f"[DEBUG] Server types response: {response.status_code}")

    if response.status_code != 200:
        print(f"Error fetching server types: {response.status_code} - {response.text}")
        return None

    server_types = response.json()['server_types']

    for st in server_types:
        if st['name'] == name:
            return st['id']

    return None

def check_availability(server_type_id, target_dc_names):
    """Check if a given server type is available in specific datacenters"""
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }

    response = requests.get('https://api.hetzner.cloud/v1/datacenters', headers=headers)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch datacenters: {response.status_code} - {response.text}")
        return []

    all_dcs = response.json().get('datacenters', [])
    available_locations = []

    for dc in all_dcs:
        if dc['name'] in target_dc_names:
            dc_id = dc['id']
            dc_detail_url = f'https://api.hetzner.cloud/v1/datacenters/{dc_id}'
            print(f"[DEBUG] Requesting: {dc_detail_url}")

            dc_response = requests.get(dc_detail_url, headers=headers)
            print(f"[DEBUG] Response {dc_response.status_code} for {dc['name']}")

            if dc_response.status_code != 200:
                print(f"[ERROR] {dc['name']}: {dc_response.status_code} - {dc_response.text}")
                continue

            dc_detail = dc_response.json()['datacenter']
            if server_type_id in dc_detail['server_types']['available']:
                available_locations.append({
                    'datacenter': dc_detail['name'],
                    'location': dc_detail['location']['name'],
                    'city': dc_detail['location']['city']
                })

    return available_locations

def main():
    print(f"Starting Hetzner cx32 monitor...")
    print(f"Checking every {CHECK_INTERVAL} seconds")
    send_notification("Hetzner Monitor", "Monitoring started for cx32")

    cx32_id = get_server_type_id(SERVER_TYPE)
    if cx32_id is None:
        print("Error: Could not find cx32 server type")
        send_notification("Hetzner Monitor Error", "Could not find cx32 server type")
        return

    print(f"Monitoring cx32 (ID: {cx32_id})")

    # Initial test for CPX21 in HEL1
    test_id = get_server_type_id(TEST_SERVER_TYPE)
    if test_id:
        test_availability = check_availability(test_id, [TEST_DATACENTER_NAME])
        if test_availability:
            print(f"[INIT TEST] {TEST_SERVER_TYPE} is available in HEL1")
        else:
            print(f"[INIT TEST] {TEST_SERVER_TYPE} is NOT available in HEL1")
    else:
        print(f"[INIT TEST] Could not get ID for {TEST_SERVER_TYPE}")

    last_available = set()

    while True:
        try:
            available = check_availability(cx32_id, DATACENTER_NAMES)
            current_available = {loc['datacenter'] for loc in available}

            new_locations = current_available - last_available

            if new_locations:
                for location in available:
                    if location['datacenter'] in new_locations:
                        message = f"cx32 available in {location['datacenter']} ({location['city']})"
                        print(f"[{datetime.now()}] {message}")
                        send_notification("Hetzner cx32 Available!", message)

            lost_locations = last_available - current_available
            if lost_locations:
                for dc in lost_locations:
                    print(f"[{datetime.now()}] cx32 no longer available in {dc}")

            last_available = current_available

            if available:
                print(f"[{datetime.now()}] cx32 available in: {', '.join(current_available)}")
            else:
                print(f"[{datetime.now()}] cx32 not available in any datacenter")

        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")
            send_notification("Hetzner Monitor Error", str(e))

        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    if not API_TOKEN:
        print("Error: HETZNER_TOKEN not found in environment")
        print("Make sure you have a .env file with HETZNER_TOKEN=your_token")
        exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped")