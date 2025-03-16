import numpy as np
import statistics
from datetime import timedelta

def analyze_heart_rate(hr_data):
    """Analyze heart rate data to determine intensity zones"""
    if not hr_data or len(hr_data) < 10:
        return None
    
    avg_hr = statistics.mean(hr_data)
    max_hr = max(hr_data)
    
    # Determine intensity based on percentage of max HR
    # Assuming max HR is the highest recorded in the activity
    # This is a simplification - ideally we'd use the user's known max HR
    
    # Calculate time spent in different zones
    # Zone 1: Recovery (< 60% of max)
    # Zone 2: Endurance (60-70% of max)
    # Zone 3: Tempo (70-80% of max)
    # Zone 4: Threshold (80-90% of max)
    # Zone 5: VO2 Max (> 90% of max)
    
    zone_counts = [0, 0, 0, 0, 0]
    
    for hr in hr_data:
        hr_percent = hr / max_hr * 100
        if hr_percent < 60:
            zone_counts[0] += 1
        elif hr_percent < 70:
            zone_counts[1] += 1
        elif hr_percent < 80:
            zone_counts[2] += 1
        elif hr_percent < 90:
            zone_counts[3] += 1
        else:
            zone_counts[4] += 1
    
    # Determine primary zone (where most time was spent)
    primary_zone = zone_counts.index(max(zone_counts)) + 1
    
    # Calculate percentage of time in each zone
    total_points = len(hr_data)
    zone_percentages = [count / total_points * 100 for count in zone_counts]
    
    return {
        'avg_hr': avg_hr,
        'max_hr': max_hr,
        'primary_zone': primary_zone,
        'zone_percentages': zone_percentages
    }

def analyze_pace(velocity_data, activity_type):
    """Analyze pace data to determine effort level"""
    if not velocity_data or len(velocity_data) < 10:
        return None
    
    # Convert velocity (m/s) to pace (min/km or min/mile)
    # For running and walking, we use min/km
    # For cycling, we use km/h
    
    avg_velocity = statistics.mean(velocity_data)
    max_velocity = max(velocity_data)
    
    # Calculate pace variations
    if len(velocity_data) > 1:
        velocity_std = statistics.stdev(velocity_data)
        velocity_changes = [abs(velocity_data[i] - velocity_data[i-1]) for i in range(1, len(velocity_data))]
        avg_change = statistics.mean(velocity_changes) if velocity_changes else 0
    else:
        velocity_std = 0
        avg_change = 0
    
    # Determine if this was interval training
    # High standard deviation and frequent changes indicate intervals
    is_interval = velocity_std > 1.0 and avg_change > 0.5
    
    # Convert to appropriate units based on activity type
    if activity_type in ['Run', 'Walk']:
        # Convert m/s to min/km
        if avg_velocity > 0:
            avg_pace_seconds = 1000 / avg_velocity  # seconds per km
            avg_pace = avg_pace_seconds / 60  # minutes per km
        else:
            avg_pace = 0
            
        pace_description = f"{int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km"
    else:  # Cycling
        # Convert m/s to km/h
        avg_speed = avg_velocity * 3.6
        pace_description = f"{avg_speed:.1f} km/h"
    
    return {
        'avg_velocity': avg_velocity,
        'max_velocity': max_velocity,
        'pace_description': pace_description,
        'is_interval': is_interval,
        'velocity_variation': velocity_std
    }

def analyze_elevation(altitude_data, grade_data=None):
    """Analyze elevation data to determine climb characteristics"""
    if not altitude_data or len(altitude_data) < 10:
        return None
    
    # Calculate total elevation gain
    elevation_changes = [max(0, altitude_data[i] - altitude_data[i-1]) for i in range(1, len(altitude_data))]
    total_gain = sum(elevation_changes)
    
    # Find significant climbs (continuous uphill sections)
    climbs = []
    current_climb = 0
    
    for i in range(1, len(altitude_data)):
        diff = altitude_data[i] - altitude_data[i-1]
        if diff > 0:
            current_climb += diff
        elif diff < -1 and current_climb > 10:  # End of climb (allowing for small flat sections)
            climbs.append(current_climb)
            current_climb = 0
        elif diff < 0 and current_climb <= 10:
            current_climb = 0
    
    # Add the last climb if it's significant
    if current_climb > 10:
        climbs.append(current_climb)
    
    # Determine if this was a hilly workout
    is_hilly = total_gain > 100  # More than 100m elevation gain
    
    # Find the biggest climb
    biggest_climb = max(climbs) if climbs else 0
    
    # Determine if this was a mountain workout
    is_mountain = biggest_climb > 300  # More than 300m continuous climb
    
    return {
        'total_gain': total_gain,
        'biggest_climb': biggest_climb,
        'is_hilly': is_hilly,
        'is_mountain': is_mountain,
        'num_significant_climbs': len(climbs)
    }

def generate_workout_title(activity, streams):
    """Generate a descriptive title based on activity data and streams"""
    if not activity or not streams:
        return "Workout"
    
    # Extract basic activity info
    activity_type = activity.get('type', 'Workout')
    distance = activity.get('distance', 0) / 1000  # Convert to km
    elapsed_time = activity.get('elapsed_time', 0)
    
    # Format time as HH:MM:SS
    time_str = str(timedelta(seconds=elapsed_time))
    if time_str.startswith('0:'):
        time_str = time_str[2:]  # Remove leading 0:
    
    # Extract streams data
    hr_data = streams.get('heartrate', {}).get('data', []) if 'heartrate' in streams else []
    velocity_data = streams.get('velocity_smooth', {}).get('data', []) if 'velocity_smooth' in streams else []
    altitude_data = streams.get('altitude', {}).get('data', []) if 'altitude' in streams else []
    grade_data = streams.get('grade_smooth', {}).get('data', []) if 'grade_smooth' in streams else []
    
    # Analyze data
    hr_analysis = analyze_heart_rate(hr_data)
    pace_analysis = analyze_pace(velocity_data, activity_type)
    elevation_analysis = analyze_elevation(altitude_data, grade_data)
    
    # Build title components
    title_parts = []
    
    # Intensity descriptor based on heart rate
    if hr_analysis:
        if hr_analysis['primary_zone'] == 1:
            title_parts.append("Recovery")
        elif hr_analysis['primary_zone'] == 2:
            title_parts.append("Endurance")
        elif hr_analysis['primary_zone'] == 3:
            title_parts.append("Tempo")
        elif hr_analysis['primary_zone'] == 4:
            title_parts.append("Threshold")
        elif hr_analysis['primary_zone'] == 5:
            title_parts.append("High Intensity")
    
    # Workout structure based on pace
    if pace_analysis and pace_analysis.get('is_interval'):
        title_parts.append("Interval")
    
    # Terrain descriptor based on elevation
    if elevation_analysis:
        if elevation_analysis.get('is_mountain'):
            title_parts.append("Mountain")
        elif elevation_analysis.get('is_hilly'):
            title_parts.append("Hilly")
    
    # Add activity type
    title_parts.append(activity_type)
    
    # Add distance
    title_parts.append(f"{distance:.1f}km")
    
    # Add pace if available
    if pace_analysis and pace_analysis.get('pace_description'):
        title_parts.append(f"at {pace_analysis['pace_description']}")
    
    # Add elevation if significant
    if elevation_analysis and elevation_analysis.get('total_gain', 0) > 50:
        title_parts.append(f"with {int(elevation_analysis['total_gain'])}m gain")
    
    # Combine all parts
    title = " ".join(title_parts)
    
    return title

def generate_title_for_activity(activity, streams):
    """Generate a title for an activity based on its data"""
    try:
        return generate_workout_title(activity, streams)
    except Exception as e:
        print(f"Error generating title: {str(e)}")
        return f"{activity.get('type', 'Workout')} {activity.get('distance', 0) / 1000:.1f}km"
