from dash import html

def create_left_top():
    return html.Div([
        html.H3("Left Top Module"),
        html.P("...")
    ], style={
        'backgroundColor': '#f2f2f2',
        'padding': '20px',
        'borderRadius': '10px',
        'height': '100%'
    }) 