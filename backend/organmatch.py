import boto3
import json
import uuid
import random
from datetime import datetime, timedelta
import os

class OrganMatchBackend:
    """Backend logic for OrganMatch operations"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        
        # AWS Configuration (optional)
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.gateway_id = os.getenv('AWS_GATEWAY_ID', '')
        self.model_id = os.getenv('AWS_MODEL_ID', '')
        self.agent_id = os.getenv('AWS_AGENT_ID', '')
        
        # Initialize AWS clients if credentials are available
        try:
            self.bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
            self.bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=self.region)
            self.aws_available = True
        except Exception:
            self.bedrock_runtime = None
            self.bedrock_agent_runtime = None
            self.aws_available = False
    
    def check_viability(self, organ_data):
        """Check organ viability - simulation mode"""
        return self._simulate_viability_check(organ_data)
    
    def _simulate_viability_check(self, organ_data):
        """Simulate organ viability checking"""
        
        organ_type = organ_data.get("type", "heart").lower()
        donation_time = organ_data.get("donation_time")
        temperature = organ_data.get("temperature", 4)
        condition_score = organ_data.get("condition_score", 85)
        
        # Calculate hours elapsed
        if donation_time:
            try:
                donation_dt = datetime.fromisoformat(donation_time.replace('Z', '+00:00'))
                current_dt = datetime.now()
                hours_elapsed = (current_dt - donation_dt).total_seconds() / 3600
            except:
                hours_elapsed = 0
        else:
            hours_elapsed = 0
        
        # Viability logic
        max_hours = {"heart": 6, "liver": 12, "kidney": 24, "lung": 8}.get(organ_type, 6)
        temp_factor = 1.0 if temperature <= 4 else 0.7
        condition_factor = condition_score / 100
        
        hours_left = max(0, (max_hours - hours_elapsed) * temp_factor * condition_factor)
        is_viable = hours_left > 0.5
        
        return {
            "is_viable": is_viable,
            "hours_left": round(hours_left, 1),
            "hours_elapsed": round(hours_elapsed, 1),
            "max_hours": max_hours,
            "recommendation": "Proceed with transport" if is_viable else "Consider alternative options",
            "urgency": "High" if hours_left < 2 else "Medium" if hours_left < 4 else "Low",
            "method": "simulation"
        }
    
    def find_matches(self, organ_data):
        """Find matching recipients - simulation mode"""
        
        # Simulate recipient database
        recipients = [
            {"id": "R045", "blood_type": "O+", "urgency": 5, "hospital": "Boston General", "distance_km": 420},
            {"id": "R012", "blood_type": "O+", "urgency": 4, "hospital": "NY Presbyterian", "distance_km": 520},
            {"id": "R089", "blood_type": "A+", "urgency": 3, "hospital": "Chicago Memorial", "distance_km": 1200},
            {"id": "R034", "blood_type": "O-", "urgency": 5, "hospital": "Miami Jackson", "distance_km": 2100},
            {"id": "R067", "blood_type": "B+", "urgency": 4, "hospital": "Seattle Medical", "distance_km": 3800},
        ]
        
        # Calculate match scores
        donor_blood_type = organ_data.get("blood_type", "O+")
        
        matches = []
        for recipient in recipients:
            # Simple matching algorithm
            blood_match = 1.0 if recipient["blood_type"] == donor_blood_type else 0.5
            urgency_score = recipient["urgency"] / 5.0
            distance_score = max(0, 1.0 - (recipient["distance_km"] / 5000))
            
            match_score = (blood_match * 0.5) + (urgency_score * 0.3) + (distance_score * 0.2)
            
            matches.append({
                **recipient,
                "match_score": round(match_score, 2),
                "status": "Best Match" if match_score > 0.8 else "Pending"
            })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
    
    def get_flight_options(self, origin, destination):
        """Get flight options - simulation mode"""
        
        flights = [
            {
                "airline": "Delta",
                "flight_number": "DL290",
                "departure": "15:00",
                "arrival": "21:20",
                "duration": "6h 20m",
                "weather_risk": "Low",
                "weather_icon": "☀️"
            },
            {
                "airline": "JetBlue",
                "flight_number": "B6408",
                "departure": "16:10",
                "arrival": "22:30",
                "duration": "6h 20m",
                "weather_risk": "Moderate",
                "weather_icon": "🌧️"
            },
            {
                "airline": "United",
                "flight_number": "UA1234",
                "departure": "14:30",
                "arrival": "20:45",
                "duration": "6h 15m",
                "weather_risk": "Low",
                "weather_icon": "☀️"
            }
        ]
        
        return flights
    
    def get_weather(self, location):
        """Get weather data - simulation mode"""
        
        weather_conditions = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Sunny"]
        
        return {
            "location": location,
            "temperature_c": random.randint(10, 25),
            "condition": random.choice(weather_conditions),
            "wind_kph": random.randint(5, 25),
            "visibility_km": random.randint(8, 15),
            "humidity": random.randint(40, 80),
            "method": "simulation"
        }
    
    def get_mock_organs(self):
        """Get mock organ data for dashboard"""
        
        current_time = datetime.now()
        
        organs = [
            {
                "id": "D001",
                "type": "Heart",
                "condition_score": 92,
                "donation_time": (current_time - timedelta(hours=2)).isoformat(),
                "hours_left": 4.0,
                "status": "healthy",
                "matched_recipient": "R045",
                "location": "UCLA Medical"
            },
            {
                "id": "D002",
                "type": "Liver",
                "condition_score": 88,
                "donation_time": (current_time - timedelta(hours=5)).isoformat(),
                "hours_left": 7.0,
                "status": "healthy",
                "matched_recipient": "R012",
                "location": "Boston General"
            },
            {
                "id": "D003",
                "type": "Kidney",
                "condition_score": 75,
                "donation_time": (current_time - timedelta(hours=18)).isoformat(),
                "hours_left": 6.0,
                "status": "expiring",
                "matched_recipient": "R089",
                "location": "Chicago Memorial"
            },
            {
                "id": "D004",
                "type": "Heart",
                "condition_score": 65,
                "donation_time": (current_time - timedelta(hours=4, minutes=30)).isoformat(),
                "hours_left": 1.5,
                "status": "critical",
                "matched_recipient": None,
                "location": "Miami Jackson"
            }
        ]
        
        return organs
