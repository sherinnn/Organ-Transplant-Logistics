# OrganMatch - AI-Powered Organ Logistics Platform

## Overview

OrganMatch is a Flask-based web application designed to optimize organ donation logistics through AI-powered matching and transport coordination. The platform provides transplant teams with tools to:

- Monitor organ viability in real-time
- Match donors with recipients using AI algorithms
- Coordinate transport logistics
- Track organs throughout the donation process

The application uses a simulated backend that can be extended with AWS Bedrock services for AI-powered matching and viability predictions.

## User Preferences

Preferred communication style: Simple, everyday language.

## Project File Structure

```
/
├── app.py                      # Main Flask application with routes
├── config.py                   # Configuration management
├── backend/
│   ├── __init__.py            # Module initialization
│   └── organmatch.py          # OrganMatch business logic
├── templates/
│   ├── base.html              # Base template with header/layout
│   ├── landing.html           # Landing page
│   ├── dashboard.html         # Mission Control Dashboard
│   ├── organ_details.html     # Organ Viability Check page
│   ├── matching.html          # Matching Engine page
│   └── transport.html         # Transport Planning page
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   ├── js/
│   │   └── main.js            # JavaScript utilities
│   └── images/                # Image assets
├── .gitignore                 # Git ignore rules
└── replit.md                  # This documentation
```

## System Architecture

### Frontend Architecture

**Technology Stack:**
- Flask (Python web framework) for server-side rendering
- Jinja2 templating engine for dynamic HTML generation
- Vanilla JavaScript for client-side interactivity
- CSS for styling with custom design system

**Design Pattern:**
- Template inheritance using `base.html` as the foundation
- Component-based layout with reusable header, sidebar, and navigation elements
- Responsive design with medical/healthcare-focused color scheme
- **Primary Colors:** #1e4d2b (dark green), #2d5a35 (medium green)
- **Accent Colors:** #e74c3c (red for alerts/icons)
- **Typography:** Bricolage Grotesque font family (Google Fonts)

**Page Structure:**
- Landing page: Marketing/overview of the platform with hero section and action cards
- Dashboard: Mission Control view showing all active organs with status indicators (green/orange/red)
- Organ Details: Form-based interface for entering organ data and running viability checks
- Matching: Interface for running AI-powered donor-recipient matching with score display
- Transport: Logistics planning and tracking interface with flight options

### Backend Architecture

**Core Components:**

1. **Flask Application (`app.py`):**
   - Main application entry point
   - Route handlers for all pages
   - Session management using Flask's built-in session support
   - CORS enabled for potential API consumption

2. **OrganMatchBackend Class (`backend/organmatch.py`):**
   - Encapsulates all business logic
   - Handles organ viability calculations
   - Manages AWS service integrations (optional)
   - Provides simulation mode when AWS credentials are unavailable

**Design Decisions:**

**Simulation-First Approach:**
- The system operates in simulation mode by default, allowing development and testing without AWS credentials
- AWS integrations are gracefully degraded - the application remains functional even when AWS services are unavailable
- This enables easier onboarding and local development

**Rationale:** Medical logistics systems require extensive testing before production deployment. A simulation mode allows developers to iterate quickly without incurring cloud costs or requiring complex AWS setup.

**Session-Based State Management:**
- Uses Flask's built-in session management with secret key configuration
- Each backend instance generates a unique session ID for tracking
- Stateless HTTP requests with minimal server-side state

**Pros:** Simple to implement, no database required for MVP
**Cons:** Sessions don't persist across server restarts, not suitable for multi-server deployments without additional session storage

### Data Storage

**Current Implementation:**
- No persistent database - all data is generated dynamically or stored in memory
- Mock data generated on-demand for demonstration purposes
- Session data stored in Flask's encrypted cookie-based sessions

**Future Considerations:**
- The architecture is designed to accommodate database integration
- OrganMatchBackend class can be extended to interact with PostgreSQL/MySQL for persistent storage
- Mock methods (`get_mock_organs()`) serve as placeholders for database queries

### Authentication & Authorization

**Current State:**
- No authentication implemented in current version
- User icon present in UI as placeholder for future user management

**Design Consideration:**
- Single-tenant design currently
- Future multi-tenant support would require role-based access control (RBAC)
- Medical data would require HIPAA-compliant authentication mechanisms

### Configuration Management

**Environment-Based Configuration (`config.py`):**
- Centralized configuration using Python class
- Environment variables for sensitive data (AWS credentials, session secrets)
- Fallback defaults for development environment
- Debug mode controlled via `FLASK_ENV` variable

**Key Configuration Areas:**
- AWS region and service IDs (optional)
- Session secret key (randomized if not provided)
- CORS headers
- Flask debug settings

## External Dependencies

### Third-Party Services

**AWS Bedrock (Optional):**
- **Purpose:** AI/ML model hosting for organ matching algorithms and viability predictions
- **Services Used:**
  - `bedrock-runtime`: For invoking AI models
  - `bedrock-agent-runtime`: For running AI agents
- **Integration Pattern:** Boto3 SDK with graceful degradation
- **Fallback:** Local simulation when credentials unavailable

**Service Availability Detection:**
The application attempts to initialize AWS clients on startup and sets an `aws_available` flag. All AWS-dependent features check this flag before attempting cloud calls.

### Python Dependencies

**Core Framework:**
- `Flask`: Web application framework
- `flask-cors`: Cross-Origin Resource Sharing support

**AWS Integration:**
- `boto3`: AWS SDK for Python (optional dependency)

**Utilities:**
- `python-dotenv`: Environment variable loading (implied by code structure)

**Built-in Libraries:**
- `json`: Data serialization
- `uuid`: Unique identifier generation
- `random`: Mock data generation
- `datetime`: Time calculations for organ viability
- `os`: Environment variable access

### Frontend Dependencies (CDN-based)

**Font Awesome 6.4.0:**
- Icon library for medical and UI icons
- Loaded via CDN

**Google Fonts (Bricolage Grotesque):**
- Custom typography for professional medical interface
- Variable font with weight range 200-800

### API Integrations

**Current State:**
- No external API integrations beyond AWS Bedrock (optional)
- Application designed to be self-contained

**Architecture Support:**
- CORS enabled for potential external API consumption
- RESTful route structure ready for API endpoints
- JSON response support via Flask's `jsonify`