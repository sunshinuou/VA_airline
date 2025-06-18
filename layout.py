from dash import html, dcc
import dash_bootstrap_components as dbc

def create_compact_layout(subgroup_options, color_options=None, pc_dimension_options=None):
    """
    Compact layout with clustering properly integrated into predictive analysis module
    """
    # Default options for parallel categories if not provided
    if not pc_dimension_options:
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
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Label("Sample Size", style={'fontWeight': 'bold', 'fontSize': '18px', 'display': 'inline-block', 'marginRight': '5px', 'verticalAlign': 'middle'}),
                            dcc.Dropdown(
                                id='sample-dropdown',
                                options=[
                                    {'label': '1K', 'value': 1000},
                                    {'label': '5K', 'value': 5000},
                                    {'label': 'All', 'value': -1}
                                ],
                                value=5000,
                                clearable=False,
                                style={
                                    'width': '60px',
                                    'fontSize': '18px',
                                    'display': 'inline-block',
                                    'height': '30px',
                                    'minHeight': '30px',
                                    'verticalAlign': 'middle'
                                }
                            )
                        ], style={'display': 'inline-block', 'verticalAlign': 'middle', 'float': 'left', 'marginTop': '15px'}),
                        html.H1("Airline Passenger Satisfaction Dashboard", 
                               style={'color': '#1a237e', 'fontWeight': 'bold', 'display': 'inline-block', 'margin': '0', 'position': 'absolute', 'left': '50%', 'transform': 'translateX(-50%)'})
                    ], style={'position': 'relative', 'height': '60px', 'marginBottom': '10px'}),
                ]),
                html.Hr()
            ])
        ]),
        
        # Two-row grid layout
        html.Div([
            # Row 1: Dataset Overview + Service Quality Radar + Service Factor Rankings
            html.Div([
                # Left: Dataset Overview
                html.Div([
                    # Title and Sample Size in header
                    html.Div([
                        html.H5("Dataset Overview", className="mb-2", style={'color': '#1a237e', 'display': 'inline-block', 'marginBottom': 0, 'fontSize': '28px', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '8px'}),
                    
                    # Summary stats (3 metrics) - Keep Passengers, Satisfaction, Avg Service
                    html.Div([
                        # Total Passengers
                        html.Div([
                            html.H4(f"0", style={'color': '#d32f2f', 'margin': '0', 'fontSize': '20px'}),
                            html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0', 'fontSize': '15px'})
                        ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
                        # Satisfaction Rate
                        html.Div([
                            html.H4(f"0%", style={'color': '#4caf50', 'margin': '0', 'fontSize': '20px'}),
                            html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0', 'fontSize': '15px'})
                        ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
                        # Avg Service Score
                        html.Div([
                            html.H4(f"0.0/5.0", style={'color': '#2196f3', 'margin': '0', 'fontSize': '20px'}),
                            html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0', 'fontSize': '15px'})
                        ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'})
                    ], id='summary-stats-container', style={'display': 'flex', 'justifyContent': 'space-between', 'minHeight': '80px', 'marginBottom': '6px'}),
                    
                    # Group by for distribution chart (direct child)
                    html.Div([
                        html.Label("Group by:", 
                                 style={
                                     'fontWeight': 'bold', 
                                     'marginBottom': '4px',
                                     'display': 'block',
                                     'color': '#1a237e',
                                     'fontSize': '23px'
                                 }),
                        dcc.Dropdown(
                            id='subgroup-dropdown-distribution',
                            options=subgroup_options,
                            value=subgroup_options[0]['value'] if subgroup_options else None,
                            clearable=False,
                            style={
                                'fontSize': '23px',
                                'marginBottom': '8px'
                            },
                            optionHeight=40,
                            maxHeight=200
                        )
                    ], style={'marginBottom': '4px'}),
                    
                    # Pie chart area
                    dcc.Graph(
                        id='distribution-chart',
                        style={
                            'width': '100%',
                            'height': '300px',
                            'marginBottom': '10px'
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="module-container", style={
                    'width': '30%',
                    'height': '60vh',
                    'float': 'left',
                    'margin': '0 1.5% 1.5% 0',
                    'padding': '15px',
                    'backgroundColor': '#fff',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'display': 'flex',
                    'flexDirection': 'column'
                }),
                
                # Middle: Service Quality Radar
                html.Div([
                    # Title area at top
                    html.Div([
                        html.H5("Service Quality Radar", 
                               style={'color': '#1a237e', 'marginBottom': '10px', 'textAlign': 'left', 'fontSize': '28px', 'fontWeight': 'bold'})
                    ]),
                    # Radar Chart area
                    html.Div([
                        dcc.Graph(
                            id='radar-chart', 
                            style={
                                'height': '400px',
                                'width': '100%'
                            },
                            config={
                                'displayModeBar': False
                            }
                        )
                    ], style={
                        'height': '400px',
                        'flex': '1',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ], className="module-container", style={
                    'width': '32%',
                    'height': '60vh',
                    'float': 'left',
                    'margin': '0 1.5% 1.5% 0',
                    'padding': '15px',
                    'backgroundColor': '#fff',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'display': 'flex',
                    'flexDirection': 'column'
                }),
                
                # Right: Service Factor Rankings Block
                html.Div([
                    # Title
                    html.Div([
                        html.H5("Service Factor Rankings (Random Forest Impact)", 
                               style={'color': '#1a237e', 'marginBottom': '10px', 'textAlign': 'left', 'fontSize': '28px', 'fontWeight': 'bold'})
                    ]),
                    
                    # Add subgroup dropdown to choose specific subgroup
                    html.Div([
                        html.Label("Select Subgroup:", style={'fontWeight': 'bold', 'color': '#1a237e', 'fontSize': '23px', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='service-factors-subgroup-dropdown',
                            options=[],  # Will be populated by callback
                            value=None,
                            clearable=False,
                            style={'fontSize': '23px', 'marginBottom': '10px'}
                        )
                    ]),
                    
                    # Subgroup info header (only Satisfaction and Avg Service - 2 metrics)
                    html.Div(
                        id='subgroup-info-header',
                        style={
                            'textAlign': 'center',
                            'marginBottom': '15px',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'borderRadius': '5px',
                            'border': '1px solid #e0e0e0'
                        }
                    ),
                    
                    # Service factors ranking chart
                    dcc.Graph(
                        id='service-factors-chart',
                        style={
                            'height': '400px',
                            'width': '100%'
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="module-container", style={
                    'width': '35%',
                    'height': '60vh',
                    'float': 'right',
                    'margin': '0 0 1.5% 0',
                    'padding': '15px',
                    'backgroundColor': '#fff',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'display': 'flex',
                    'flexDirection': 'column'
                })
            ], style={'overflow': 'hidden'}),
            
            # Row 2: Parallel Categories + Predictive Analysis (with Clustering inside)
            html.Div([
                # Left: Parallel Categories
                html.Div([
                    html.H5("Parallel Categories", className="mb-3", style={'color': '#1a237e', 'fontSize': '28px', 'fontWeight': 'bold'}),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Category Flow (max 6):", style={'fontWeight': 'bold', 'color': '#1a237e', 'fontSize': '23px'}),
                            dcc.Dropdown(
                                id='pc-dimensions-dropdown',
                                options=pc_dimension_options,
                                value=['Customer Type', 'Class', 'Type of Travel', 'Satisfaction'],
                                multi=True,
                                clearable=False,
                                maxHeight=300,
                                style={'fontSize': '23px'}
                            )
                        ], width=12)
                    ], className="mb-2"),
                    dcc.Graph(
                        id='parallel-coords',
                        style={
                            'height': '300px',
                            'width': '700px',
                            'marginLeft': 'auto',
                            'marginRight': 'auto',
                            'display': 'block'
                        }
                    )
                ], className="module-container", style={
                    'width': '55%',
                    'height': '50vh',
                    'float': 'left',
                    'margin': '0 1.5% 0 0',
                    'padding': '15px',
                    'backgroundColor': '#fff',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                
                # Right: Passenger Segmentation Analysis (containing clustering functionality)
                html.Div([
                    html.H5("Passenger Segmentation Analysis", className="mb-3", style={'color': '#1a237e', 'fontSize': '28px', 'fontWeight': 'bold'}),
                    
                    # Chart selection dropdown for clustering analysis
                    html.Div([
                        html.Label("Analysis Type:", style={'fontWeight': 'bold', 'fontSize': '23px', 'color': '#1a237e'}),
                        dcc.Dropdown(
                            id='clustering-chart-selector',
                            options=[
                                {'label': 'Passenger Segments (PCA)', 'value': 'pca_scatter'},
                                {'label': 'Segment Comparison', 'value': 'cluster_comparison'},
                                {'label': 'Service Profiles', 'value': 'cluster_profiles'}
                            ],
                            value='pca_scatter',
                            clearable=False,
                            style={'fontSize': '23px', 'marginBottom': '10px'}
                        )
                    ], style={'marginBottom': '15px'}),
                    
                    # Clustering chart area
                    dcc.Graph(
                        id='clustering-chart',
                        style={'height': '280px', 'marginBottom': '15px'},
                        config={'displayModeBar': False}
                    )
                ], className="module-container", style={
                    'width': '43%', 
                    'height': '50vh',
                    'float': 'right',
                    'margin': '0', 
                    'padding': '15px',
                    'backgroundColor': '#fff', 
                    'border': '1px solid #ddd',
                    'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflowY': 'auto'
                })
            ], style={'overflow': 'hidden'})
        ])
    ], fluid=True, style={'padding': '20px'})