from dash import html, dcc
import dash_bootstrap_components as dbc

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
                    # Title and Sample Size in header
                    html.Div([
                        html.H5("Dataset Overview", className="mb-2", style={'color': '#1a237e', 'display': 'inline-block'}),
                        html.Div([
                            html.Label("Sample Size", style={'fontWeight': 'bold', 'fontSize': '12px', 'display': 'inline-block', 'marginRight': '5px'}),
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
                                    'fontSize': '12px',
                                    'display': 'inline-block',
                                    'height': '30px',
                                    'minHeight': '30px'
                                }
                            )
                        ], style={'float': 'right', 'marginTop': '5px'})
                    ], style={'marginBottom': '15px'}),
                    
                    # Summary stats container with three statistics
                    html.Div(id='summary-stats-container', children=[
                        html.Div([
                            # Total Passengers
                            html.Div([
                                html.H4(f"0", style={'color': '#d32f2f', 'margin': '0', 'fontSize': '20px'}),
                                html.P("Total Passengers", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
                            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
                            
                            # Satisfaction Rate
                            html.Div([
                                html.H4(f"0%", style={'color': '#4caf50', 'margin': '0', 'fontSize': '20px'}),
                                html.P("Satisfaction Rate", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
                            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'}),
                            
                            # Avg Service Score
                            html.Div([
                                html.H4(f"0.0/5.0", style={'color': '#2196f3', 'margin': '0', 'fontSize': '20px'}),
                                html.P("Avg Service Score", style={'color': '#666', 'margin': '5px 0', 'fontSize': '12px'})
                            ], style={'textAlign': 'center', 'padding': '10px', 'width': '33.33%'})
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '250px'}),
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
                                id='subgroup-dropdown-distribution',
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
                            'zIndex': '1000'})
                    ]),
                ], className="module-container", style={
                    'width': '30%', 'height': '60vh', 'float': 'left', 
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
                        ], width=12)
                    ], className="mb-2"),
                    dcc.Graph(id='parallel-coords', style={'height': '250px'})
                ], className="module-container", style={
                    'width': '67%', 'height': '60vh', 'float': 'right',
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