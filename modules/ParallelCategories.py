import plotly.graph_objects as go
from utils import get_display_name, get_display_value
import pandas as pd


def create_parallel_categories_chart(df, selected_dimensions, sample_size=5000):
    """
    Create parallel categories chart for categorical airline data with full width and complete labels
    """
    if sample_size > 0 and len(df) > sample_size:
        plot_data = df.sample(n=sample_size, random_state=42)
    else:
        plot_data = df.copy()
    
    # define available categorical dimensions 
    available_dimensions = {
        'Customer Type': 'Customer Type',
        'Gender': 'Gender', 
        'Class': 'Class',
        'Type of Travel': 'Type of Travel',
        'Age Group': 'Age_Group',
        'Satisfaction': 'satisfaction',
        'Departure Delay Category': 'Departure_Delay_Category',
        'Arrival Delay Category': 'Arrival_Delay_Category'
    }
    
    # filter selected dimensions
    valid_dimensions = []
    valid_labels = []
    
    for dim in selected_dimensions:
        if dim in available_dimensions and available_dimensions[dim] in plot_data.columns:
            valid_dimensions.append(available_dimensions[dim])
            valid_labels.append(dim)
    
    # If no valid dimensions, use default
    if not valid_dimensions:
        default_dims = ['Customer Type', 'Class', 'Type of Travel', 'satisfaction']
        valid_dimensions = [d for d in default_dims if d in plot_data.columns]
        valid_labels = [d.replace('_', ' ').title() for d in valid_dimensions]
    
    if not valid_dimensions:
        return go.Figure().add_annotation(
            text="No suitable categorical dimensions available",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14)
        )
    
    dimensions = []
    
    for i, (col, label) in enumerate(zip(valid_dimensions, valid_labels)):
        values = plot_data[col].astype(str).fillna('Unknown')
        
        display_values = values.map(get_display_value)
        
        # Get unique categories
        if pd.api.types.is_categorical_dtype(plot_data[col]):
            categories = plot_data[col].cat.categories.tolist()
            display_categories = [get_display_value(str(cat)) for cat in categories]
        else:
            display_categories = display_values.unique().tolist()
        
        dimensions.append(dict(
            values=display_values, 
            label=get_display_name(label),
            categoryorder='array',
            categoryarray=display_categories
        ))
    
    # create parallel categories chart
    fig = go.Figure(data=[go.Parcats(
        dimensions=dimensions,
        line=dict(
            colorscale='viridis',
            showscale=True,
            shape='hspline'
        ),
        hoveron='color',
        hoverinfo='count+probability',
        labelfont=dict(size=16, family="Arial"),
        tickfont=dict(size=15, family="Arial"),
        arrangement='freeform'
    )])
    
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),  
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True
    )
    
    return fig