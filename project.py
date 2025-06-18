import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from layout import create_compact_layout
from preprocess import preprocess_airline_data
from modules.RaderChart import create_radar_chart
from modules.ParallelCoordinates import create_parallel_coordinates
from modules.Distribution import create_distribution_chart
from modules.ParallelCoordinates import create_parallel_coordinates, create_parallel_categories_chart
from modules.ServiceFactor import create_service_factors_chart, generate_subgroup_info_header
from modules.clustering import CustomerSegmentationAnalyzer
from utils import get_display_name

def generate_subgroup_info_header_simple(df, group_col='Class', selected_subgroup=None):
    """
    Generate simplified header with only Satisfaction and Avg Service (2 metrics)
    """
    if group_col not in df.columns:
        return html.Div("No subgroup data available", style={'color': '#666'})
    
    # Preserve categorical order if available
    if pd.api.types.is_categorical_dtype(df[group_col]):
        groups = df[group_col].cat.categories.tolist()
    else:
        groups = df[group_col].unique().tolist()
    
    if selected_subgroup is None or selected_subgroup not in groups:
        selected_subgroup = groups[0] if groups else None
    
    if selected_subgroup is None:
        return html.Div("No subgroup selected", style={'color': '#666'})
    
    # Get subgroup data
    subgroup_data = df[df[group_col] == selected_subgroup]
    
    if len(subgroup_data) == 0:
        return html.Div(f"No data for {selected_subgroup}", style={'color': '#666'})
    
    # Calculate metrics - only 2 metrics
    satisfaction_rate = 0
    if 'satisfaction' in df.columns:
        satisfaction_rate = (subgroup_data['satisfaction'] == 'satisfied').mean() * 100
    
    service_score = 0
    if 'Service_Quality_Score' in subgroup_data.columns:
        service_score = subgroup_data['Service_Quality_Score'].mean()
    
    return html.Div([
        html.H6(f"Analysis for {selected_subgroup}", 
               style={'color': '#1a237e', 'marginBottom': '8px', 'fontWeight': 'bold', 'fontSize': '22px'}),
        html.Div([
            html.Span(f"Satisfaction: {satisfaction_rate:.1f}%", 
                     style={'marginRight': '20px', 'fontSize': '20px', 'color': '#4caf50'}),
            html.Span(f"Avg Service: {service_score:.2f}/5.0", 
                     style={'fontSize': '20px', 'color': '#2196f3'})
        ])
    ])

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
    
    # Initialize clustering analyzer (global for callbacks)
    global clustering_analyzer
    clustering_analyzer = CustomerSegmentationAnalyzer(df, service_attributes)
    clustering_analyzer.perform_kmeans_clustering()
    clustering_analyzer.perform_pca_analysis()
    
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
    
    # Define parallel categories dimension options
    pc_dimension_options = [
        {'label': 'Customer Type', 'value': 'Customer Type'},
        {'label': 'Gender', 'value': 'Gender'},
        {'label': 'Class', 'value': 'Class'},
        {'label': 'Type of Travel', 'value': 'Type of Travel'},
        {'label': 'Age Group', 'value': 'Age Group'},
        {'label': 'Satisfaction', 'value': 'Satisfaction'},
        {'label': 'Departure Delay Category', 'value': 'Departure Delay Category'},
        {'label': 'Arrival Delay Category', 'value': 'Arrival Delay Category'}
    ]
    
    # Set the compact layout with proper options
    app.layout = create_compact_layout(subgroup_options, None, pc_dimension_options)
    
    # Callback for clustering chart updates
    @app.callback(
        Output('clustering-chart', 'figure'),
        [Input('clustering-chart-selector', 'value'),
         Input('sample-dropdown', 'value')]
    )
    def update_clustering_analysis(chart_type, sample_size):
        # Apply sampling if requested
        if sample_size > 0 and len(df) > sample_size:
            sampled_df = df.sample(n=sample_size, random_state=42)
            # Recreate analyzer with sampled data
            temp_analyzer = CustomerSegmentationAnalyzer(sampled_df, service_attributes)
            temp_analyzer.perform_kmeans_clustering()
            temp_analyzer.perform_pca_analysis()
        else:
            temp_analyzer = clustering_analyzer
        # Create chart based on selection
        chart_fig = temp_analyzer.create_cluster_visualization(chart_type)
        return chart_fig
    
    # Callback to populate service factors subgroup dropdown based on Dataset Overview group by
    @app.callback(
        [Output('service-factors-subgroup-dropdown', 'options'),
         Output('service-factors-subgroup-dropdown', 'value')],
        [Input('subgroup-dropdown-distribution', 'value')]
    )
    def update_service_factors_subgroup_options(selected_group_col):
        if selected_group_col and selected_group_col in df.columns:
            # Preserve categorical order if available
            if pd.api.types.is_categorical_dtype(df[selected_group_col]):
                unique_values = df[selected_group_col].cat.categories.tolist()
            else:
                unique_values = df[selected_group_col].unique().tolist()
            options = [{'label': val, 'value': val} for val in unique_values]
            default_value = unique_values[0] if unique_values else None
            return options, default_value
        else:
            return [], None

    # Main callback for all charts - responds to both dropdowns independently
    @app.callback(
        [Output('radar-chart', 'figure'),
         Output('parallel-coords', 'figure'),
         Output('summary-stats-container', 'children'),
         Output('distribution-chart', 'figure'),
         Output('service-factors-chart', 'figure'),
         Output('subgroup-info-header', 'children')],
        [Input('subgroup-dropdown-distribution', 'value'),  # Dataset Overview
         Input('sample-dropdown', 'value'),
         Input('pc-dimensions-dropdown', 'value'),
         Input('service-factors-subgroup-dropdown', 'options'),
         Input('service-factors-subgroup-dropdown', 'value')]
    )
    def update_charts(dataset_subgroup, sample_size, selected_dimensions, subgroup_options, selected_specific_subgroup):
        if sample_size > 0 and len(df) > sample_size:
            sampled_df = df.sample(n=sample_size, random_state=42)
        else:
            sampled_df = df.copy()

        if (not selected_specific_subgroup) and subgroup_options:
            selected_specific_subgroup = subgroup_options[0]['value']

        distribution_fig = create_distribution_chart(sampled_df, group_col=dataset_subgroup)
        radar_fig = create_radar_chart(sampled_df, service_attributes, dataset_subgroup)
        parallel_fig = create_parallel_categories_chart(sampled_df, selected_dimensions, sample_size)
        
        total_passengers = len(sampled_df)
        summary_items = html.Div([
            html.Div([
                html.H4(f"{total_passengers:,}", style={'color': '#d32f2f', 'margin': '0', 'fontSize': '20px'}),
                html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0', 'fontSize': '20px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            html.Div([
                html.H4(f"{(sampled_df['satisfaction'] == 'satisfied').mean() * 100:.1f}%", 
                       style={'color': '#4caf50', 'margin': '0', 'fontSize': '20px'}),
                html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0', 'fontSize': '20px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
            html.Div([
                html.H4(f"{sampled_df['Service_Quality_Score'].mean():.2f}/5.0", 
                       style={'color': '#2196f3', 'margin': '0', 'fontSize': '20px'}),
                html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0', 'fontSize': '20px'})
            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'minHeight': '80px', 'marginBottom': '6px'})
        
        # Service Factor Rankings
        service_factors_fig = create_service_factors_chart(
            sampled_df, 
            service_attributes, 
            group_col=dataset_subgroup,
            selected_subgroup=selected_specific_subgroup,
            chart_type='rf_importance'
        )
        subgroup_info = generate_subgroup_info_header_simple(
            sampled_df, 
            group_col=dataset_subgroup,
            selected_subgroup=selected_specific_subgroup
        )
        return (radar_fig, parallel_fig, summary_items, distribution_fig, 
                service_factors_fig, subgroup_info)
    
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
    
    # Create and run the Dash app
    app = create_dash_app(df_processed, service_attributes)
    
    print("\n=== STARTING DASH SERVER ===")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("Press Ctrl+C to stop the server")
    
    # Use app.run() instead of app.run_server() for newer Dash versions
    app.run(debug=True)

if __name__ == "__main__":
    main()