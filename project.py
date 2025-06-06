import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from layout import create_compact_layout
from modules.RaderChart import create_radar_chart
from modules.ParallelCoordinates import create_parallel_coordinates
from modules.Distribution import create_distribution_chart
from preprocess import preprocess_airline_data
from modules.mlPredictor import ml

def load_and_validate_data(file_path):
    """
    Load and validate the airline dataset
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_dash_app(df, service_attributes):
    """
    Create comprehensive Dash application with error handling
    """
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Prepare dropdown options based on available columns
    subgroup_options = []
    potential_subgroups = [
        ('Gender', 'Gender'),
        ('Customer Type', 'Customer Type'),
        ('Age Group', 'Age_Group'),
        ('Travel Class', 'Class'),
        ('Type of Travel', 'Type of Travel'),
        ('Travel Experience', 'Travel_Experience')
    ]
    
    for label, value in potential_subgroups:
        if value in df.columns:
            subgroup_options.append({'label': label, 'value': value})
    
    color_options = [
        {'label': 'Satisfaction', 'value': 'satisfaction'},
        {'label': 'Age', 'value': 'Age'},
        {'label': 'Flight Distance', 'value': 'Flight Distance'}
    ]
    
    # Filter color options based on available columns
    color_options = [opt for opt in color_options if opt['value'] in df.columns or opt['value'] == 'satisfaction']
    
    # Set the compact layout
    app.layout = create_compact_layout(subgroup_options, color_options)
    
    # Store the prediction function and accuracy in app.server
    accuracy, predict_func = ml(df, service_attributes)
    app.server.predict_func = predict_func
    app.server.prediction_accuracy = accuracy
    
    # Callbacks
    @app.callback(
        [Output('radar-chart', 'figure'),
         Output('parallel-coords', 'figure'),
         Output('summary-stats-container', 'children'),
         Output('distribution-chart', 'figure')],
        [Input('subgroup-dropdown', 'value'),
         Input('color-dropdown', 'value'),
         Input('sample-dropdown', 'value'),
         Input('subgroup-dropdown-distribution', 'value')]
    )
    def update_charts(selected_subgroup, color_by, sample_size, dist_group_col):
        # Apply sampling to the entire dataset
        if sample_size > 0 and len(df) > sample_size:
            sampled_df = df.sample(n=sample_size, random_state=42)
        else:
            sampled_df = df.copy()
        
        # Update distribution chart with sampled data
        distribution_fig = create_distribution_chart(sampled_df, group_col=dist_group_col)
        # Update radar chart with sampled data
        radar_fig = create_radar_chart(sampled_df, service_attributes, selected_subgroup)
        # Update parallel coordinates with sampled data
        parallel_fig = create_parallel_coordinates(sampled_df, service_attributes, color_by, sample_size)
        # Generate summary statistics using sampled data
        total_passengers = len(sampled_df)
        # Return the summary stats div directly (no wrapper id)
        summary_items = html.Div([
            html.Div([
                html.H4(f"{total_passengers:,}", style={'color': '#d32f2f', 'margin': '0', 'fontSize': '20px'}),
                html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            html.Div([
                html.H4(f"{(sampled_df['satisfaction'] == 'satisfied').mean() * 100:.1f}%", 
                       style={'color': '#4caf50', 'margin': '0', 'fontSize': '20px'}),
                html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            html.Div([
                html.H4(f"{sampled_df['Service_Quality_Score'].mean():.2f}/5.0", 
                       style={'color': '#2196f3', 'margin': '0', 'fontSize': '20px'}),
                html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'minHeight': '80px', 'marginBottom': '6px'})
        return radar_fig, parallel_fig, summary_items, distribution_fig
    
    @app.callback(
        Output('prediction-result', 'children'),
        [Input('predict-button', 'n_clicks')],
        [dash.State('gender-dropdown', 'value'),
         dash.State('age-input', 'value'),
         dash.State('customer-type-dropdown', 'value'),
         dash.State('travel-type-dropdown', 'value'),
         dash.State('class-dropdown', 'value'),
         dash.State('flight-distance-input', 'value'),
         dash.State('departure-delay-input', 'value'),
         dash.State('arrival-delay-input', 'value'),
         dash.State('wifi-service-slider', 'value'),
         dash.State('time-convenient-slider', 'value'),
         dash.State('online-booking-slider', 'value'),
         dash.State('gate-location-slider', 'value'),
         dash.State('food-drink-slider', 'value'),
         dash.State('online-boarding-slider', 'value'),
         dash.State('seat-comfort-slider', 'value'),
         dash.State('entertainment-slider', 'value'),
         dash.State('onboard-service-slider', 'value'),
         dash.State('leg-room-slider', 'value'),
         dash.State('baggage-slider', 'value'),
         dash.State('checkin-slider', 'value'),
         dash.State('inflight-service-slider', 'value'),
         dash.State('cleanliness-slider', 'value')]
    )
    def update_prediction(n_clicks, gender, age, customer_type, travel_type, class_type,
                         flight_distance, departure_delay, arrival_delay,
                         wifi_service, time_convenient, online_booking, gate_location,
                         food_drink, online_boarding, seat_comfort, entertainment,
                         onboard_service, leg_room, baggage, checkin,
                         inflight_service, cleanliness):
        if n_clicks is None:
            return ""
        
        # Create passenger info dictionary
        passenger_info = {
            'Gender': gender,
            'Age': age,
            'Customer Type': customer_type,
            'Type of Travel': travel_type,
            'Class': class_type,
            'Flight Distance': flight_distance,
            'Departure Delay in Minutes': departure_delay,
            'Arrival Delay in Minutes': arrival_delay,
            'Inflight wifi service': wifi_service,
            'Departure/Arrival time convenient': time_convenient,
            'Ease of Online booking': online_booking,
            'Gate location': gate_location,
            'Food and drink': food_drink,
            'Online boarding': online_boarding,
            'Seat comfort': seat_comfort,
            'Inflight entertainment': entertainment,
            'On-board service': onboard_service,
            'Leg room service': leg_room,
            'Baggage handling': baggage,
            'Checkin service': checkin,
            'Inflight service': inflight_service,
            'Cleanliness': cleanliness
        }
        
        # Get prediction
        prediction = app.server.predict_func(passenger_info)
        accuracy = app.server.prediction_accuracy
        
        # Return formatted result
        return dbc.Row([
            dbc.Col([
                html.H4("Prediction Result:", style={'marginBottom': '10px', 'fontSize': '18px'}),
                html.H3(prediction, style={
                    'color': '#4caf50' if prediction == 'Satisfied' else '#f44336',
                    'fontWeight': 'bold',
                    'fontSize': '22px'
                })
            ], width=7),
            dbc.Col([
                html.H4("Prediction Accuracy:", style={'marginBottom': '10px', 'fontSize': '16px'}),
                html.H3(f"{accuracy*100:.2f}%", style={
                    'color': '#1a237e',
                    'fontWeight': 'bold',
                    'fontSize': '20px'
                })
            ], width=5, style={'textAlign': 'right', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'})
        ], align='center')
    
    return app

# ===== MAIN EXECUTION =====
def main():
    """
    Main function to run the application
    """
    print("Starting Airline Satisfaction Analysis Dashboard...")
    
    # Load data
    file_path = "dataset/data2.csv"
    
    df = load_and_validate_data(file_path)
    if df is None:
        print("Failed to load data. Please check the file path.")
        return
    
    # Preprocess the data
    df_processed, service_attributes = preprocess_airline_data(df)
    if df_processed is None:
        print("Failed to preprocess data.")
        return
    
    # machine learning model training and prediction
    accuracy, predict_func = ml(df_processed, service_attributes)
    print(f"\nXGBoost model accuracy on test set: {accuracy:.4f}")
    # example passenger info
    sample_passenger = {
        'Gender': 'Male',
        'Age': 35,
        'Customer Type': 'Loyal Customer',
        'Type of Travel': 'Business travel',
        'Class': 'Business',
        'Flight Distance': 1000,
        'Departure Delay in Minutes': 10,
        'Arrival Delay in Minutes': 3,
        'Inflight wifi service': 4,
        'Departure/Arrival time convenient': 3,
        'Ease of Online booking': 4,
        'Gate location': 2,
        'Food and drink': 1,
        'Online boarding': 2,
        'Seat comfort': 1,
        'Inflight entertainment': 0,
        'On-board service': 2,
        'Leg room service': 1,
        'Baggage handling':1,
        'Checkin service': 2,
        'Inflight service': 1,
        'Cleanliness': 1
    }
    pred = predict_func(sample_passenger)
    print(f"Prediction for sample passenger: {pred}")

    # Create and run the Dash app
    app = create_dash_app(df_processed, service_attributes)
    
    print("\n=== STARTING DASH SERVER ===")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("Press Ctrl+C to stop the server")
    
    # Use app.run() instead of app.run_server() for newer Dash versions
    app.run(debug=True)

if __name__ == "__main__":
    main()

