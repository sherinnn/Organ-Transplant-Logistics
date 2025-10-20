#!/usr/bin/env python3
"""
OrganMatch Frontend - Flask Application
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import os
from config import Config
from backend import OrganMatchBackend

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize OrganMatch backend
organmatch = OrganMatchBackend()

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    """Mission Control Dashboard"""
    organs = organmatch.get_mock_organs()
    
    # Calculate summary stats
    total_organs = len(organs)
    active_organs = sum(1 for o in organs if o['status'] == 'healthy')
    in_transit = sum(1 for o in organs if o.get('matched_recipient'))
    expiring_soon = sum(1 for o in organs if o['status'] in ['expiring', 'critical'])
    
    stats = {
        'total_organs': total_organs,
        'active_organs': active_organs,
        'in_transit': in_transit,
        'expiring_soon': expiring_soon,
        'avg_match_time': '2.3 hrs',
        'success_rate': '94%'
    }
    
    return render_template('dashboard.html', organs=organs, stats=stats)

@app.route('/organ-details')
def organ_details():
    """Organ Details & Viability Check"""
    organ_id = request.args.get('id', '')
    return render_template('organ_details.html', organ_id=organ_id)

@app.route('/api/check-viability', methods=['POST'])
def check_viability():
    """API endpoint for viability check"""
    data = request.json
    
    organ_data = {
        'type': data.get('organ_type', 'heart'),
        'donation_time': data.get('donation_time'),
        'temperature': float(data.get('temperature', 4)),
        'condition_score': int(data.get('condition_score', 85))
    }
    
    result = organmatch.check_viability(organ_data)
    return jsonify(result)

@app.route('/matching')
def matching():
    """Matching Engine"""
    organ_id = request.args.get('id', '')
    return render_template('matching.html', organ_id=organ_id)

@app.route('/api/find-matches', methods=['POST'])
def find_matches():
    """API endpoint for finding matches"""
    data = request.json
    
    organ_data = {
        'type': data.get('organ_type', 'heart'),
        'blood_type': data.get('blood_type', 'O+')
    }
    
    matches = organmatch.find_matches(organ_data)
    return jsonify({'matches': matches})

@app.route('/transport')
def transport():
    """Transport Planning"""
    organ_id = request.args.get('id', 'D003')
    recipient_id = request.args.get('recipient', 'R045')
    
    return render_template('transport.html', organ_id=organ_id, recipient_id=recipient_id)

@app.route('/api/flight-options', methods=['POST'])
def flight_options():
    """API endpoint for flight options"""
    data = request.json
    
    origin = data.get('origin', 'Los Angeles')
    destination = data.get('destination', 'Boston')
    
    flights = organmatch.get_flight_options(origin, destination)
    return jsonify({'flights': flights})

@app.route('/api/weather', methods=['POST'])
def weather():
    """API endpoint for weather data"""
    data = request.json
    location = data.get('location', 'Boston')
    
    weather_data = organmatch.get_weather(location)
    return jsonify(weather_data)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'aws_available': organmatch.aws_available
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
