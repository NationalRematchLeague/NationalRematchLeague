from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Airtable configuration
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN', 'your_api_key_here')
BASE_ID = 'appwknGToAyZyO50F'
TABLE_ID = 'tblXUBdMdUjq0lDav'
AIRTABLE_API_URL = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}'

@app.route('/api/today-games', methods=['GET'])
def get_today_games():
    try:
        # Get today's date in the format Airtable uses (YYYY-MM-DD)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Query Airtable - filter for today's date
        headers = {
            'Authorization': f'Bearer {AIRTABLE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Fetch ALL records with pagination
        all_records = []
        offset = None
        
        while True:
            params = {}
            if offset:
                params['offset'] = offset
            
            response = requests.get(AIRTABLE_API_URL, headers=headers, params=params)
            
            if response.status_code != 200:
                return jsonify({'error': 'Failed to fetch from Airtable', 'details': response.text}), response.status_code
            
            data = response.json()
            records = data.get('records', [])
            all_records.extend(records)
            
            # Check if there are more pages
            offset = data.get('offset')
            if not offset:
                break
        
        print(f"Total records fetched: {len(all_records)}")
        
        # Filter games for today
        today_games = []
        for record in all_records:
            fields = record.get('fields', {})
            start_date = fields.get('Start Date', '')
            
            # Debug: Print all field names
            if start_date.startswith(today):
                print(f"\n=== Fields for {fields.get('Event', 'Unknown')} ===")
                print(f"Available fields: {list(fields.keys())}")
                for key, value in fields.items():
                    print(f"  {key}: {value}")
            
            # Check if this game is today
            if start_date.startswith(today):
                game = {
                    'id': record['id'],
                    'event': fields.get('Event', 'Match'),
                    'startDate': fields.get('Start Date', ''),
                    'status': fields.get('Status', 'Scheduled'),
                    'primetime': fields.get('Primetime', False),
                    'primetimeSelect': fields.get('Primetime Select', '')
                }
                today_games.append(game)
                print(f"Added game: {game['event']}")
        
        # Sort by start date/time
        today_games.sort(key=lambda x: x['startDate'])
        
        print(f"Today's games count: {len(today_games)}")
        
        return jsonify({
            'date': today,
            'games': today_games,
            'count': len(today_games)
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
