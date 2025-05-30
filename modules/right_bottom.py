from dash import html

def create_right_bottom():
    return html.Div([
        html.H3("Right Bottom Module"),
        html.P("...")
    ], style={
        'backgroundColor': '#f2f2f2',
        'padding': '20px',
        'borderRadius': '10px',
        'height': '100%'
    }) 