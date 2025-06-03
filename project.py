import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from layout import create_compact_layout
from modules.RaderChart import create_radar_chart
from modules.ParallelCoordinates import create_parallel_coordinates
from preprocess import preprocess_airline_data

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
    
    # Callbacks
    @app.callback(
        [Output('radar-chart', 'figure'),
         Output('parallel-coords', 'figure'),
         Output('summary-stats-container', 'children')],
        [Input('subgroup-dropdown', 'value'),
         Input('color-dropdown', 'value'),
         Input('sample-dropdown', 'value')]
    )
    def update_charts(selected_subgroup, color_by, sample_size):
        # Apply sampling to the entire dataset
        if sample_size > 0 and len(df) > sample_size:
            sampled_df = df.sample(n=sample_size, random_state=42)
        else:
            sampled_df = df.copy()
        
        # Update radar chart with sampled data
        radar_fig = create_radar_chart(sampled_df, service_attributes, selected_subgroup)
        
        # Update parallel coordinates with sampled data
        parallel_fig = create_parallel_coordinates(sampled_df, service_attributes, color_by, sample_size)
        
        # Generate summary statistics using sampled data
        total_passengers = len(sampled_df)
        
        # Create one-row layout with three statistics
        summary_items = html.Div([
            # Total Passengers
            html.Div([
                html.H4(f"{total_passengers:,}", style={'color': '#d32f2f', 'margin': '0', 'fontSize': '20px'}),
                html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            
            # Satisfaction Rate
            html.Div([
                html.H4(f"{(sampled_df['satisfaction'] == 'satisfied').mean() * 100:.1f}%", 
                       style={'color': '#4caf50', 'margin': '0', 'fontSize': '20px'}),
                html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            
            # Avg Service Score
            html.Div([
                html.H4(f"{sampled_df['Service_Quality_Score'].mean():.2f}/5.0", 
                       style={'color': '#2196f3', 'margin': '0', 'fontSize': '20px'}),
                html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '250px'})
        
        return radar_fig, parallel_fig, summary_items
    
    return app

# ===== MAIN EXECUTION =====
def main():
    """
    Main function to run the application
    """
    print("Starting Airline Satisfaction Analysis Dashboard...")
    
    # Load data
    file_path = "dataset/data1.csv"
    
    df = load_and_validate_data(file_path)
    if df is None:
        print("Failed to load data. Please check the file path.")
        return
    
    # Preprocess the data
    df_processed, service_attributes = preprocess_airline_data(df)
    if df_processed is None:
        print("Failed to preprocess data.")
        return
    
    # Create and run the Dash app
    app = create_dash_app(df_processed, service_attributes)
    
    print("\n=== STARTING DASH SERVER ===")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("Press Ctrl+C to stop the server")
    
    # Use app.run() instead of app.run_server() for newer Dash versions
    app.run(debug=True)

if __name__ == "__main__":
    main()

