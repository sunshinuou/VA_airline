from dash import html, dcc
import dash_bootstrap_components as dbc
from modules.left_top import create_left_top
from modules.left_bottom import create_left_bottom
from modules.right_top import create_right_top
from modules.right_bottom import create_right_bottom

def create_layout():
    horizontal_gap = 3
    vertical_gap = 10
    padding = 8
    extra_margin = 30
         
    return html.Div([
        # top decoration
        html.Div(
            html.H1("Airline Satisfaction", 
                   style={
                       'textAlign': 'center',
                       'color': '#1a237e',
                       'margin': '0',
                       'padding': '10px'
                   }),
            style={
                'backgroundColor': '#e3f2fd',
                'width': '100%',
                'height': '60px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }
        ),
        # 4 main modules
        html.Div([
            html.Div(
                create_left_top(),
                style={
                    'position': 'absolute',
                    'left': '0',
                    'top': '0',
                    'width': f'calc(33% - {horizontal_gap/2}px)',
                    'height': f'calc(50% - {vertical_gap/2}px - {extra_margin}px)',
                    'padding': f'{padding}px',
                    'boxSizing': 'border-box',
                }
            ), 
            html.Div(
                create_right_top(),
                style={
                    'position': 'absolute',
                    'left': f'calc(33% + {horizontal_gap/2}px)',
                    'top': '0',
                    'width': f'calc(67% - {horizontal_gap/2}px)',
                    'height': f'calc(50% - {vertical_gap/2}px - {extra_margin}px)',
                    'padding': f'{padding}px',
                    'boxSizing': 'border-box',
                }
            ),
            html.Div(
                create_left_bottom(),
                style={
                    'position': 'absolute',
                    'left': '0',
                    'top': f'calc(50% + {vertical_gap/2}px)',
                    'width': f'calc(33% - {horizontal_gap/2}px)',
                    'height': f'calc(50% - {vertical_gap/2}px - {extra_margin}px)',
                    'padding': f'{padding}px',
                    'boxSizing': 'border-box',
                }
            ),
            html.Div(
                create_right_bottom(),
                style={
                    'position': 'absolute',
                    'left': f'calc(33% + {horizontal_gap/2}px)',
                    'top': f'calc(50% + {vertical_gap/2}px)',
                    'width': f'calc(67% - {horizontal_gap/2}px)',
                    'height': f'calc(50% - {vertical_gap/2}px - {extra_margin}px)',
                    'padding': f'{padding}px',
                    'boxSizing': 'border-box',
                }
            ),
        ], style={
            'position': 'relative',
            'width': '100vw',
            'height': 'calc(100vh - 60px)',
            'overflow': 'hidden',
            'background': 'transparent',
            'top': '0',
        })
    ], style={
        'width': '100vw',
        'height': '100vh',
        'margin': '0',
        'padding': '0',
        'overflow': 'hidden',
        'background': '#fff',
    })