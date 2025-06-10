import plotly.graph_objects as go

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
                    label=dim,
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
