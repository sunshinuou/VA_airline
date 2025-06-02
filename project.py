import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

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

def preprocess_airline_data(df):
    """
    Robust data preprocessing with error handling
    """
    if df is None:
        return None, None
    
    # Create a copy to avoid modifying original data
    df_processed = df.copy()
    
    print("=== DATA PREPROCESSING ===")
    print(f"Original shape: {df_processed.shape}")
    
    # 1. Handle missing values
    print(f"\nMissing values before preprocessing:")
    missing_summary = df_processed.isnull().sum()
    for col, count in missing_summary[missing_summary > 0].items():
        print(f"  {col}: {count} ({count/len(df_processed)*100:.1f}%)")
    
    # Handle arrival delay missing values
    if 'Arrival Delay in Minutes' in df_processed.columns:
        before_fill = df_processed['Arrival Delay in Minutes'].isnull().sum()
        df_processed['Arrival Delay in Minutes'] = df_processed['Arrival Delay in Minutes'].fillna(0)
        print(f"Filled {before_fill} missing arrival delay values with 0")
    
    # Remove rows with missing satisfaction data (critical for analysis)
    if 'satisfaction' in df_processed.columns:
        before_drop = len(df_processed)
        df_processed = df_processed.dropna(subset=['satisfaction'])
        after_drop = len(df_processed)
        if before_drop != after_drop:
            print(f"Dropped {before_drop - after_drop} rows with missing satisfaction data")
    
    # 2. Data type conversions and cleaning
    print(f"\nProcessed shape: {df_processed.shape}")
    
    # Ensure satisfaction is properly encoded
    if 'satisfaction' in df_processed.columns:
        df_processed['satisfaction_binary'] = (df_processed['satisfaction'] == 'satisfied').astype(int)
        satisfaction_counts = df_processed['satisfaction'].value_counts()
        print(f"Satisfaction distribution: {dict(satisfaction_counts)}")
    
    # Create age groups for better analysis
    if 'Age' in df_processed.columns:
        df_processed['Age_Group'] = pd.cut(df_processed['Age'], 
                                         bins=[0, 25, 40, 60, 100], 
                                         labels=['Young (≤25)', 'Adult (26-40)', 'Middle-aged (41-60)', 'Senior (>60)'])
    
    # Create delay categories
    if 'Departure Delay in Minutes' in df_processed.columns:
        df_processed['Departure_Delay_Category'] = pd.cut(df_processed['Departure Delay in Minutes'],
                                                         bins=[-1, 0, 15, 60, float('inf')],
                                                         labels=['No Delay', 'Short (1-15min)', 'Medium (16-60min)', 'Long (>60min)'])
    
    if 'Arrival Delay in Minutes' in df_processed.columns:
        df_processed['Arrival_Delay_Category'] = pd.cut(df_processed['Arrival Delay in Minutes'],
                                                       bins=[-1, 0, 15, 60, float('inf')],
                                                       labels=['No Delay', 'Short (1-15min)', 'Medium (16-60min)', 'Long (>60min)'])
    
    # 3. Define service attributes for analysis
    potential_service_attributes = [
        'Inflight wifi service', 'Departure/Arrival time convenient', 
        'Ease of Online booking', 'Gate location', 'Food and drink',
        'Online boarding', 'Seat comfort', 'Inflight entertainment',
        'On-board service', 'Leg room service', 'Baggage handling',
        'Checkin service', 'Inflight service', 'Cleanliness'
    ]
    
    # Only include attributes that exist in the dataset
    service_attributes = [attr for attr in potential_service_attributes if attr in df_processed.columns]
    print(f"\nFound {len(service_attributes)} service attributes:")
    for attr in service_attributes:
        print(f"  - {attr}")
    
    # 4. Validate and clean service ratings
    for attr in service_attributes:
        # Check the range of values
        min_val = df_processed[attr].min()
        max_val = df_processed[attr].max()
        print(f"{attr}: range {min_val} to {max_val}")
        
        # Clip values to valid range if needed (assuming 1-5 or 0-5 scale)
        if min_val >= 0 and max_val <= 5:
            df_processed[attr] = df_processed[attr].clip(0, 5)
        elif min_val >= 1 and max_val <= 5:
            df_processed[attr] = df_processed[attr].clip(1, 5)
    
    # 5. Create composite scores
    if service_attributes:
        df_processed['Service_Quality_Score'] = df_processed[service_attributes].mean(axis=1)
        print(f"Created Service Quality Score (avg: {df_processed['Service_Quality_Score'].mean():.2f})")
    
    # 6. Feature engineering for subgroup analysis
    if 'Type of Travel' in df_processed.columns and 'Class' in df_processed.columns:
        df_processed['Travel_Experience'] = df_processed['Type of Travel'] + '_' + df_processed['Class']
    
    print("=== PREPROCESSING COMPLETE ===")
    return df_processed, service_attributes

def create_radar_chart(df, service_attributes, subgroup_col, subgroup_values=None):
    """
    Create interactive radar chart for service attributes by subgroup
    """
    if not service_attributes or subgroup_col not in df.columns:
        return go.Figure().add_annotation(text="No data available for radar chart", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    if subgroup_values is None:
        subgroup_values = df[subgroup_col].unique()
        # Limit to 4 subgroups for better readability
        if len(subgroup_values) > 4:
            subgroup_values = subgroup_values[:4]
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1[:len(subgroup_values)]
    
    for i, subgroup in enumerate(subgroup_values):
        # Filter data for this subgroup
        subgroup_data = df[df[subgroup_col] == subgroup]
        
        if len(subgroup_data) == 0:
            continue
        
        # Calculate mean scores for each service attribute
        scores = [subgroup_data[attr].mean() for attr in service_attributes]
        
        # Add trace to radar chart
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],  # Close the polygon
            theta=service_attributes + [service_attributes[0]],
            fill='toself',
            name=f'{subgroup} (n={len(subgroup_data)})',
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    # Determine the scale based on actual data
    all_scores = []
    for attr in service_attributes:
        all_scores.extend(df[attr].dropna().tolist())
    
    if all_scores:
        min_score = min(all_scores)
        max_score = max(all_scores)
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[min_score, max_score],
                    tickvals=list(range(int(min_score), int(max_score)+1)),
                    ticktext=[f"Level {i}" for i in range(int(min_score), int(max_score)+1)]
                ),
                angularaxis=dict(
                    tickfont=dict(size=9)  # Smaller font for better fit
                )
            ),
            showlegend=True,
            legend=dict(
                x=1.05,  # Move legend outside the plot area
                y=0.5,
                xanchor='left',
                yanchor='middle',
                font=dict(size=10)
            ),
            title=f"Service Quality Radar Chart by {subgroup_col}",
            height=180,  # Further reduced to make more room for dropdown
            margin=dict(l=30, r=80, t=40, b=20)  # More right margin for legend
        )
    
    return fig

def create_parallel_coordinates(df, service_attributes, color_by='satisfaction', sample_size=5000):
    """
    Create interactive parallel coordinates plot with error handling
    """
    if not service_attributes:
        return go.Figure().add_annotation(text="No service attributes available", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Sample the data if requested
    if sample_size > 0 and len(df) > sample_size:
        plot_data = df.sample(n=sample_size, random_state=42)
    else:
        plot_data = df.copy()
    
    # Add numerical columns for visualization
    dimensions = []
    
    # Add key operational metrics if they exist
    if 'Flight Distance' in plot_data.columns:
        dimensions.append(dict(label="Flight Distance", values=plot_data['Flight Distance']))
    if 'Departure Delay in Minutes' in plot_data.columns:
        dimensions.append(dict(label="Departure Delay", values=plot_data['Departure Delay in Minutes']))
    if 'Arrival Delay in Minutes' in plot_data.columns:
        dimensions.append(dict(label="Arrival Delay", values=plot_data['Arrival Delay in Minutes']))
    
    # Add service attributes (limit to key ones to avoid overcrowding)
    key_services = ['Seat comfort', 'Food and drink', 'Inflight entertainment', 
                   'Inflight wifi service', 'Cleanliness']
    
    for service in key_services:
        if service in service_attributes and service in plot_data.columns:
            service_data = plot_data[service].dropna()
            if len(service_data) > 0:
                dimensions.append(dict(
                    label=service, 
                    values=plot_data[service], 
                    range=[service_data.min(), service_data.max()]
                ))
    
    if not dimensions:
        return go.Figure().add_annotation(text="No valid dimensions for parallel coordinates", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    # Color mapping
    if color_by == 'satisfaction' and 'satisfaction_binary' in plot_data.columns:
        color_values = plot_data['satisfaction_binary']
        colorscale = [[0, 'red'], [1, 'green']]
        colorbar_title = "Satisfaction"
    elif color_by in plot_data.columns:
        color_values = plot_data[color_by]
        colorscale = 'Viridis'
        colorbar_title = color_by
    else:
        color_values = [1] * len(plot_data)
        colorscale = 'Blues'
        colorbar_title = "Data Points"
    
    fig = go.Figure(data=go.Parcoords(
        line=dict(color=color_values,
                 colorscale=colorscale,
                 showscale=True,
                 colorbar=dict(title=colorbar_title)),
        dimensions=dimensions
    ))
    
    fig.update_layout(
        #title="Parallel Coordinates: Service Factors vs Satisfaction",
        height=250,
        margin=dict(l=50, r=50, t=40, b=50)
    )
    
    return fig

def create_radar_chart(df, service_attributes, subgroup_col, subgroup_values=None):
    """
    Create interactive radar chart for service attributes by subgroup
    """
    if not service_attributes or subgroup_col not in df.columns:
        return go.Figure().add_annotation(text="No data available for radar chart", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    if subgroup_values is None:
        subgroup_values = df[subgroup_col].unique()
        # Limit to 4 subgroups for better readability
        if len(subgroup_values) > 4:
            subgroup_values = subgroup_values[:4]
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1[:len(subgroup_values)]
    
    for i, subgroup in enumerate(subgroup_values):
        # Filter data for this subgroup
        subgroup_data = df[df[subgroup_col] == subgroup]
        
        if len(subgroup_data) == 0:
            continue
        
        # Calculate mean scores for each service attribute
        scores = [subgroup_data[attr].mean() for attr in service_attributes]
        
        # Add trace to radar chart
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],  # Close the polygon
            theta=service_attributes + [service_attributes[0]],
            fill='toself',
            name=f'{subgroup} (n={len(subgroup_data)})',
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    # Determine the scale based on actual data
    all_scores = []
    for attr in service_attributes:
        all_scores.extend(df[attr].dropna().tolist())
    
    if all_scores:
        min_score = min(all_scores)
        max_score = max(all_scores)
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[min_score, max_score],
                    tickvals=list(range(int(min_score), int(max_score)+1)),
                    ticktext=[f"Level {i}" for i in range(int(min_score), int(max_score)+1)],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=9),
                    rotation=0,
                    direction="clockwise"
                )
            ),
            showlegend=True,
            legend=dict(
                x=0.5,  
                y=-0.15,  # Position below the chart
                xanchor='center',
                yanchor='top',
                font=dict(size=10),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='rgba(0,0,0,0.3)',
                borderwidth=1,
                orientation='h'  # Horizontal orientation to save space
            ),
            title=None,  # Remove title since we have it in the layout
            height=350,  # Bigger chart height
            margin=dict(l=80, r=80, t=20, b=80),  # Balanced margins
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            uirevision='constant'  # This prevents the chart from resetting on updates
        )
    
    return fig


def create_compact_layout(subgroup_options, color_options):
    """
    Compact layout with dropdown below radar chart
    """
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Airline Passenger Satisfaction Dashboard", 
                       className="text-center mb-3",
                       style={'color': '#1a237e', 'fontWeight': 'bold'}),
                html.Hr()
            ])
        ]),
        
        # Two-row grid layout
        html.Div([
            # Row 1: Dataset Overview + Parallel Coordinates
            html.Div([
                # Left: Dataset Overview
                html.Div([
                    html.H5("Dataset Overview", className="mb-3", style={'color': '#1a237e'}),
                    html.Div(id='summary-stats-container', children=[
                        html.H3("Loading...", style={'textAlign': 'center', 'color': '#666'})
                    ], style={
                        'height': '250px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ], className="module-container", style={
                    'width': '30%', 'height': '45vh', 'float': 'left', 
                    'margin': '0 1.5% 1.5% 0', 'padding': '15px',
                    'backgroundColor': '#fff', 'border': '1px solid #ddd',
                    'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                
                # Right: Parallel Coordinates
                html.Div([
                    html.H5("Parallel Coordinates", className="mb-3", style={'color': '#1a237e'}),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Color by:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='color-dropdown',
                                options=color_options,
                                value=color_options[0]['value'] if color_options else None,
                                clearable=False
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Sample:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='sample-dropdown',
                                options=[
                                    {'label': '1K', 'value': 1000},
                                    {'label': '5K', 'value': 5000},
                                    {'label': 'All', 'value': -1}
                                ],
                                value=5000,
                                clearable=False
                            )
                        ], width=6)
                    ], className="mb-2"),
                    dcc.Graph(id='parallel-coords', style={'height': '250px'})
                ], className="module-container", style={
                    'width': '67%', 'height': '45vh', 'float': 'right',
                    'margin': '0 0 1.5% 0', 'padding': '15px',
                    'backgroundColor': '#fff', 'border': '1px solid #ddd',
                    'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            ], style={'overflow': 'hidden'}),
            
            # Row 2: Radar Chart + Predictive Analysis
            html.Div([
                # Left: Radar Chart with dropdown at top
                html.Div([
                    # Title and dropdown area at top
                    html.Div([
                        html.H5("Service Quality Radar", 
                               style={'color': '#1a237e', 'marginBottom': '10px', 'textAlign': 'center'}),
                        html.Div([
                            html.Label("Group by:", 
                                     style={
                                         'fontWeight': 'bold', 
                                         'marginBottom': '5px',
                                         'display': 'block',
                                         'color': '#1a237e',
                                         'fontSize': '14px'
                                     }),
                            dcc.Dropdown(
                                id='subgroup-dropdown',
                                options=subgroup_options,
                                value=subgroup_options[0]['value'] if subgroup_options else None,
                                clearable=False,
                                style={
                                    'fontSize': '13px'
                                },
                                optionHeight=40,  # Taller options for better visibility
                                maxHeight=200  # Limit dropdown height but allow scrolling
                            )
                        ], style={
                            'marginBottom': '15px',
                            'position': 'relative',
                            'zIndex': '1000'
                        })
                    ]),
                    
                    # Radar Chart area
                    html.Div([
                        dcc.Graph(
                            id='radar-chart', 
                            style={
                                'height': '380px',  # Increased height for bigger chart
                                'width': '100%'
                            },
                            config={
                                'displayModeBar': False  # Hide toolbar for cleaner look
                            }
                        )
                    ], style={
                        'height': '380px',
                        'flex': '1'  # Take remaining space
                    })
                ], className="module-container", style={
                    'width': '30%', 
                    'height': '70vh',  # Increased container height
                    'float': 'left',
                    'margin': '0 1.5% 0 0', 
                    'padding': '15px',
                    'backgroundColor': '#fff', 
                    'border': '1px solid #ddd',
                    'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflow': 'visible',  # Allow dropdown to extend outside
                    'position': 'relative',
                    'zIndex': '100',
                    'display': 'flex',
                    'flexDirection': 'column'
                }),
                
                # Right: Predictive Analysis
                html.Div([
                    html.H5("Predictive Analysis", className="mb-3", style={'color': '#1a237e'}),
                    html.Div([
                        html.H6("What-if scenarios coming soon...", 
                              style={'textAlign': 'center', 'color': '#666', 'marginTop': '180px'})
                    ], style={'textAlign': 'center'})
                ], className="module-container", style={
                    'width': '67%', 
                    'height': '70vh',  # Matched height with radar chart container
                    'float': 'right',
                    'margin': '0', 
                    'padding': '15px',
                    'backgroundColor': '#fff', 
                    'border': '1px solid #ddd',
                    'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            ], style={'overflow': 'hidden'})
        ])
    ], fluid=True, style={'padding': '20px'})

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
        # Update radar chart
        radar_fig = create_radar_chart(df, service_attributes, selected_subgroup)
        
        # Update parallel coordinates
        parallel_fig = create_parallel_coordinates(df, service_attributes, color_by, sample_size)
        
        # Generate summary statistics
        total_passengers = len(df)
        
        summary_items = [
            html.Div([
                html.H2(f"{total_passengers:,}", style={'color': '#1a237e', 'margin': '0'}),
                html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0 15px 0'})
            ], style={'textAlign': 'center'})
        ]
        
        if 'satisfaction' in df.columns:
            satisfaction_rate = (df['satisfaction'] == 'satisfied').mean() * 100
            summary_items.append(
                html.Div([
                    html.H3(f"{satisfaction_rate:.1f}%", style={'color': '#4caf50', 'margin': '0'}),
                    html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0 15px 0'})
                ], style={'textAlign': 'center'})
            )
        
        if 'Service_Quality_Score' in df.columns:
            avg_service_score = df['Service_Quality_Score'].mean()
            summary_items.append(
                html.Div([
                    html.H4(f"{avg_service_score:.2f}/5.0", style={'color': '#2196f3', 'margin': '0'}),
                    html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0 15px 0'})
                ], style={'textAlign': 'center'})
            )
        
        if service_attributes:
            top_services = df[service_attributes].mean().nlargest(3).index.tolist()
            summary_items.append(
                html.Div([
                    html.H6("Top Service Factors:", style={'color': '#1a237e', 'margin': '10px 0 5px 0'}),
                    html.Ul([
                        html.Li(service, style={'fontSize': '12px'}) 
                        for service in top_services
                    ], style={'textAlign': 'left', 'color': '#666'})
                ], style={'marginTop': '15px'})
            )
        
        return radar_fig, parallel_fig, summary_items
    
    return app

# ===== MAIN EXECUTION =====
def main():
    """
    Main function to run the application
    """
    print("Starting Airline Satisfaction Analysis Dashboard...")
    
    # Load your data - UPDATE THIS PATH
    file_path = r"D:\visual airline\test.csv"  # Change this to your actual file path
    
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

