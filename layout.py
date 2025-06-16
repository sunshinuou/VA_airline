from dash import html, dcc
import dash_bootstrap_components as dbc

def create_compact_layout(subgroup_options, color_options=None, pc_dimension_options=None):
    """
    Compact layout with pie chart and detailed service analysis
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
    
    # We don't need color options for parallel categories, so remove the color dropdown
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Label("Sample Size", style={'fontWeight': 'bold', 'fontSize': '12px', 'display': 'inline-block', 'marginRight': '5px', 'verticalAlign': 'middle'}),
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
                        html.H5("Dataset Overview", className="mb-2", style={'color': '#1a237e', 'display': 'inline-block', 'marginBottom': 0})
                    ], style={'marginBottom': '8px'}),
                    
                    # Summary stats (3 metrics) - Keep Passengers, Satisfaction, Avg Service
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
                    ], id='summary-stats-container', style={'display': 'flex', 'justifyContent': 'space-between', 'minHeight': '80px', 'marginBottom': '6px'}),
                    
                    # Group by for distribution chart (direct child)
                    html.Div([
                        html.Label("Group by:", 
                                 style={
                                     'fontWeight': 'bold', 
                                     'marginBottom': '4px',
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
                                'fontSize': '13px',
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
                    # Title and dropdown area at top
                    html.Div([
                        html.H5("Service Quality Radar", 
                               style={'color': '#1a237e', 'marginBottom': '10px', 'textAlign': 'left'}),
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
                                optionHeight=40,
                                maxHeight=200
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
                                'height': '380px',
                                'width': '100%'
                            },
                            config={
                                'displayModeBar': False
                            }
                        )
                    ], style={
                        'height': '380px',
                        'flex': '1'
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
                               style={'color': '#1a237e', 'marginBottom': '10px', 'textAlign': 'left'})
                    ]),
                    
                    # Add group by dropdown for Service Factor Rankings
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
                            id='service-factors-group-dropdown',
                            options=subgroup_options,
                            value=subgroup_options[0]['value'] if subgroup_options else None,
                            clearable=False,
                            style={
                                'fontSize': '13px',
                                'marginBottom': '10px'
                            },
                            optionHeight=40,
                            maxHeight=200
                        )
                    ], style={
                        'marginBottom': '15px',
                        'position': 'relative',
                        'zIndex': '1000'
                    }),
                    
                    # Add subgroup dropdown to choose specific subgroup
                    html.Div([
                        html.Label("Select Subgroup:", style={'fontSize': '12px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                        dcc.Dropdown(
                            id='service-factors-subgroup-dropdown',
                            options=[],  # Will be populated by callback
                            value=None,
                            clearable=False,
                            style={'fontSize': '12px', 'marginBottom': '10px'}
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
            
            # Row 2: Parallel Categories + Predictive Analysis
            html.Div([
                # Left: Parallel Categories
                html.Div([
                    html.H5("Parallel Categories", className="mb-3", style={'color': '#1a237e'}),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Category Flow (max 6):", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='pc-dimensions-dropdown',
                                options=pc_dimension_options,
                                value=['Customer Type', 'Class', 'Type of Travel', 'Satisfaction'],
                                multi=True,
                                clearable=False,
                                maxHeight=200
                            )
                        ], width=12)
                    ], className="mb-2"),
                    dcc.Graph(id='parallel-coords', style={'height': '300px', 'width': '100%'})
                ], className="module-container", style={
                    'width': '50%', 
                    'height': '50vh',
                    'float': 'left',
                    'margin': '0 1.5% 0 0', 
                    'padding': '15px',
                    'backgroundColor': '#fff', 
                    'border': '1px solid #ddd',
                    'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                }),
                # Right: Predictive Analysis
                html.Div([
                    html.H5("Predictive Analysis", className="mb-3", style={'color': '#1a237e'}),
                    html.Div([
                        # Personal Info Section
                        html.Div([
                            html.H6("Personal Information", style={'color': '#1a237e', 'marginBottom': '15px', 'fontSize': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Gender", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='gender-dropdown',
                                        options=[
                                            {'label': 'Male', 'value': 'Male'},
                                            {'label': 'Female', 'value': 'Female'}
                                        ],
                                        value='Male',
                                        style={'fontSize': '13px'}
                                    )
                                ], width=6, style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),
                                dbc.Col([
                                    html.Label("Age", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Input(
                                        id='age-input',
                                        type='number',
                                        value=35,
                                        min=0,
                                        max=120,
                                        style={'fontSize': '13px', 'width': '100%'}
                                    )
                                ], width=6, style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'})
                            ], className="mb-2", align='center'),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Customer Type", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='customer-type-dropdown',
                                        options=[
                                            {'label': 'Loyal Customer', 'value': 'Loyal Customer'},
                                            {'label': 'Disloyal Customer', 'value': 'Disloyal Customer'}
                                        ],
                                        value='Loyal Customer',
                                        style={'fontSize': '13px'}
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Type of Travel", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='travel-type-dropdown',
                                        options=[
                                            {'label': 'Business travel', 'value': 'Business travel'},
                                            {'label': 'Personal Travel', 'value': 'Personal Travel'}
                                        ],
                                        value='Business travel',
                                        style={'fontSize': '13px'}
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Class", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Dropdown(
                                        id='class-dropdown',
                                        options=[
                                            {'label': 'Business', 'value': 'Business'},
                                            {'label': 'Eco', 'value': 'Eco'},
                                            {'label': 'Eco Plus', 'value': 'Eco Plus'}
                                        ],
                                        value='Business',
                                        style={'fontSize': '13px'}
                                    )
                                ], width=4)
                            ], className="mb-3", align='center')
                        ], className="mb-4"),
                        
                        # Flight Info Section
                        html.Div([
                            html.H6("Flight Information", style={'color': '#1a237e', 'marginBottom': '15px', 'fontSize': '16px'}),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Flight Distance (miles)", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Input(
                                        id='flight-distance-input',
                                        type='number',
                                        value=1000,
                                        min=0,
                                        style={'fontSize': '13px', 'width': '100%'}
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Departure Delay (minutes)", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Input(
                                        id='departure-delay-input',
                                        type='number',
                                        value=0,
                                        min=0,
                                        style={'fontSize': '13px', 'width': '100%'}
                                    )
                                ], width=4),
                                dbc.Col([
                                    html.Label("Arrival Delay (minutes)", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                    dcc.Input(
                                        id='arrival-delay-input',
                                        type='number',
                                        value=0,
                                        min=0,
                                        style={'fontSize': '13px', 'width': '100%'}
                                    )
                                ], width=4)
                            ], className="mb-3", align='center')
                        ], className="mb-4"),
                        
                        # Service Quality Section (abbreviated for brevity)
                        html.Div([
                            html.H6("Service Quality Rating", style={'color': '#1a237e', 'marginBottom': '15px', 'fontSize': '16px'}),
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Inflight wifi service", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='wifi-service-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=4,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Departure/Arrival time convenient", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='time-convenient-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=3,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Ease of Online booking", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='online-booking-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=4,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Gate location", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='gate-location-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=2,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Food and drink", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='food-drink-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Online boarding", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='online-boarding-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=2,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Seat comfort", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='seat-comfort-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Inflight entertainment", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='entertainment-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=0,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("On-board service", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='onboard-service-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=2,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Leg room service", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='leg-room-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Baggage handling", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='baggage-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Checkin service", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='checkin-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=2,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3)
                                ], className="mb-3"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Inflight service", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='inflight-service-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Cleanliness", style={'fontSize': '13px', 'fontWeight': 'bold'}),
                                        dcc.Slider(
                                            id='cleanliness-slider',
                                            min=0,
                                            max=5,
                                            step=1,
                                            value=1,
                                            marks={i: str(i) for i in range(6)},
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ], width=3)
                                ], className="mb-3")
                            ])
                        ], className="mb-4"),
                        
                        # Predict Button and Result
                        html.Div([
                            dbc.Button(
                                "Predict Satisfaction",
                                id="predict-button",
                                className="mb-3",
                                style={'width': '100%', 'backgroundColor': '#1a237e', 'borderColor': '#1a237e'}
                            ),
                            html.Div(
                                id="prediction-result",
                                style={
                                    'textAlign': 'center',
                                    'fontSize': '20px',
                                    'fontWeight': 'bold',
                                    'marginTop': '10px'
                                }
                            )
                        ])
                    ], style={'padding': '20px'})
                ], className="module-container", style={
                    'width': '47%', 
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