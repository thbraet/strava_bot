# Strava Activity Filter

A web application that automatically hides shorter activities from your Strava feed while keeping them public. Perfect for Strava users who track all their activities but only want to share significant workouts with their followers.

## Features

- Connect your Strava account
- Customize thresholds for different activity types (Run, Ride, Walk)
- Automatically hide activities below your thresholds from your followers' feed
- Activity tracking and statistics dashboard

## How It Works

1. The app registers a webhook with Strava
2. When a new activity is created on Strava, the webhook notifies our app
3. The app checks the activity duration against your thresholds
4. If the activity is shorter than your threshold, the app automatically sets the "Hide from Feed" flag

## Setup Instructions

### Prerequisites

- Python 3.8+
- A Strava account
- A Strava API application (create one at https://www.strava.com/settings/api)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/strava-activity-filter.git
   cd strava-activity-filter
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env` and update the values:
   ```
   cp .env.example .env
   ```

5. Set up the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the development server:
   ```
   python run.py
   ```

7. Register the webhook with Strava (one-time setup):
   ```
   curl -X POST https://www.strava.com/api/v3/push_subscriptions \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     -F callback_url=https://your-app-domain.com/webhook \
     -F verify_token=YOUR_VERIFICATION_TOKEN
   ```

### Deployment

The app can be deployed to various hosting platforms:

#### Render.com (Recommended)
1. Create an account at render.com
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the environment variables
5. Deploy

#### Railway.app
1. Create an account at railway.app
2. Create a new project
3. Connect your GitHub repository
4. Set the environment variables
5. Deploy

#### Heroku
1. Install the Heroku CLI
2. Log in to Heroku: `heroku login`
3. Create a new app: `heroku create`
4. Push to Heroku: `git push heroku main`
5. Set environment variables: `heroku config:set VARIABLE_NAME=value`

## Usage

1. Visit the homepage and click "Connect with Strava"
2. Authorize the application to access your Strava account
3. Adjust the thresholds for each activity type in Settings
4. Start recording activities on Strava - the app will automatically process them

## Security Considerations

- The app uses refresh tokens to maintain access to your Strava account
- No activity data is stored except for basic metadata (name, type, duration)
- Your Strava credentials are never stored or accessed

## License

This project is licensed under the MIT License - see the LICENSE file for details.