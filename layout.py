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
                        html.H5("Dataset Overview", className="mb-2", style={'color': '#1a237e', 'display': 'inline-block', 'marginBottom': 0}),
                        html.Div([
                            html.Label("Sample Size", style={'fontWeight': 'bold', 'fontSize': '12px', 'display': 'inline-block', 'marginRight': '5px', 'marginBottom': 0}),
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
                                    'marginBottom': 0
                                }
                            )
                        ], style={'float': 'right', 'marginTop': '5px', 'marginBottom': 0})
                    ], style={'marginBottom': '8px'}),
                    # Summary stats (direct child, with id for dynamic update)
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
                                'marginBottom': 0
                            },
                            optionHeight=40,
                            maxHeight=200
                        )
                    ], style={'marginBottom': '4px'}),
                    # distribution chart area (flex: 1)
                    dcc.Graph(
                        id='distribution-chart',
                        style={
                            'width': '100%',
                            'flex': '1',
                            'minHeight': '200px',
                            'marginBottom': 0
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
                        
                        # Service Quality Section
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
                                    ], width=4),
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
                                    ], width=4),
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
                                    ], width=4)
                                ], className="mb-3"),
                                dbc.Row([
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
                                    ], width=4),
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
                                    ], width=4),
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
                                    ], width=4)
                                ], className="mb-3"),
                                dbc.Row([
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
                                    ], width=4),
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
                                    ], width=4),
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
                                    ], width=4)
                                ], className="mb-3"),
                                dbc.Row([
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
                                    ], width=4),
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
                                    ], width=4),
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
                                    ], width=4)
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
                                    ], width=4),
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
                                    ], width=4)
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
                    'width': '67%', 
                    'height': '70vh',
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