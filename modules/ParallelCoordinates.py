import plotly.graph_objects as go
from utils import get_display_name, get_display_value
import pandas as pd

def create_parallel_coordinates(df, service_attributes, color_by='satisfaction', sample_size=5000, selected_dimensions=None):
    """
    Create interactive parallel coordinates plot with error handling
    Args:
        df: DataFrame containing the data
        service_attributes: List of service attributes
        color_by: Column to color the lines by
        sample_size: Number of samples to display
        selected_dimensions: List of selected dimensions to display (max 8)
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
    
    # Define all possible dimensions
    all_dimensions = {
        'Flight Distance': 'Flight Distance',
        'Departure Delay': 'Departure Delay in Minutes',
        'Arrival Delay': 'Arrival Delay in Minutes',
        'Seat comfort': 'Seat comfort',
        'Food and drink': 'Food and drink',
        'Inflight entertainment': 'Inflight entertainment',
        'Inflight wifi service': 'Inflight wifi service',
        'Cleanliness': 'Cleanliness',
        'Online boarding': 'Online boarding',
        'Gate location': 'Gate location',
        'On-board service': 'On-board service',
        'Leg room service': 'Leg room service',
        'Baggage handling': 'Baggage handling',
        'Checkin service': 'Checkin service',
        'Inflight service': 'Inflight service',
        'Departure/Arrival time convenient': 'Departure/Arrival time convenient',
        'Ease of Online booking': 'Ease of Online booking'
    }
    
    # If no dimensions are selected, use default ones
    if not selected_dimensions:
        selected_dimensions = ['Flight Distance', 'Departure Delay', 'Arrival Delay', 
                             'Seat comfort', 'Food and drink', 'Inflight entertainment']
    
    # Limit to 8 dimensions
    selected_dimensions = selected_dimensions[:8]
    
    # Add selected dimensions
    for dim in selected_dimensions:
        if dim in all_dimensions and all_dimensions[dim] in plot_data.columns:
            col_name = all_dimensions[dim]
            data = plot_data[col_name].dropna()
            if len(data) > 0:
                dimensions.append(dict(
                    label=get_display_name(dim),
                    values=plot_data[col_name],
                    range=[data.min(), data.max()]
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
        height=200,  # Reduced height
        margin=dict(l=50, r=50, t=40, b=50)
    )
    
    return fig

def create_parallel_categories_chart(df, selected_dimensions, sample_size=5000):
    """
    Create parallel categories chart for categorical airline data
    """
    # Sample the data if needed
    if sample_size > 0 and len(df) > sample_size:
        plot_data = df.sample(n=sample_size, random_state=42)
    else:
        plot_data = df.copy()
    
    # Define available categorical dimensions for airline data
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
    
    # Filter selected dimensions to only include available ones
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
    
    # Prepare dimension data for parallel categories
    dimensions = []
    
    for i, (col, label) in enumerate(zip(valid_dimensions, valid_labels)):
        # Convert to string and handle missing values
        values = plot_data[col].astype(str).fillna('Unknown')
        # Map values for display
        display_values = values.map(get_display_value)
        # Get unique categories - preserve categorical order if available
        if pd.api.types.is_categorical_dtype(plot_data[col]):
            # For categorical data, use the categories in their defined order
            categories = plot_data[col].cat.categories.tolist()
            # Map the categories to display values
            display_categories = [get_display_value(str(cat)) for cat in categories]
        else:
            # For non-categorical data, use natural order (don't sort alphabetically)
            display_categories = display_values.unique().tolist()
        
        dimensions.append(dict(
            values=display_values,
            label=get_display_name(label),
            categoryorder='array',
            categoryarray=display_categories
        ))
    
    # Create parallel categories chart
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
        tickfont=dict(size=16, family="Arial"),
        arrangement='freeform'
    )])
    
    fig.update_layout(
        height=400,
        width=850,
        margin=dict(l=10, r=10, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig