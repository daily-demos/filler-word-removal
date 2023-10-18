"""This module handles all Daily REST API operations."""
import datetime
import json
import os

import requests

DAILY_API_URL = 'https://api.daily.co/v1'


def fetch_recordings():
    """Fetches all Daily recordings is a Daily API key is configured"""
    daily_api_key = os.getenv("DAILY_API_KEY")
    if not daily_api_key:
        raise Exception("Daily API key not configured in server environment")

    headers = {'Authorization': f'Bearer {daily_api_key}'}
    url = f'{DAILY_API_URL}/recordings'

    res = requests.get(url, headers=headers, timeout=5)
    if not res.ok:
        raise Exception(
            f'Failed to fetch recordings; return code {res.status_code}; {res.text}')
    data = json.loads(res.text)
    recordings = data['data']
    finished_recordings = []
    for r in recordings:
        start = r['start_ts']
        duration = r['duration']
        d = datetime.datetime.fromtimestamp(start)
        timestamp = d + datetime.timedelta(0, duration)
        recording = {
            'id': r['id'],
            'room_name': r['room_name'],
            'timestamp': timestamp
        }
        finished_recordings.append(recording)
    return finished_recordings


def get_access_link(recording_id):
    """Fetches access link for provided Daily recording ID"""
    daily_api_key = os.getenv("DAILY_API_KEY")
    if not daily_api_key:
        raise Exception("Daily API key not configured in server environment")

    url = f'{DAILY_API_URL}/recordings/{recording_id}/access-link'
    headers = {'Authorization': f'Bearer {daily_api_key}'}

    res = requests.get(url, headers=headers, timeout=5)
    if not res.ok:
        raise Exception(
            f'Failed to get recording access link; return code {res.status_code}')
    data = json.loads(res.text)
    download_link = data['download_link']
    return download_link
