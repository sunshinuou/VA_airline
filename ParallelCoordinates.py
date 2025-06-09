import plotly.graph_objects as go

def create_parallel_coordinates(df, service_attributes, color_by='satisfaction', sample_size=5000):
    """
    Create interactive parallel coordinates plot with error handling
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
    
    # Add key operational metrics if they exist
    if 'Flight Distance' in plot_data.columns:
        dimensions.append(dict(label="Flight Distance", values=plot_data['Flight Distance']))
    if 'Departure Delay in Minutes' in plot_data.columns:
        dimensions.append(dict(label="Departure Delay", values=plot_data['Departure Delay in Minutes']))
    if 'Arrival Delay in Minutes' in plot_data.columns:
        dimensions.append(dict(label="Arrival Delay", values=plot_data['Arrival Delay in Minutes']))
    
    # Add service attributes (limit to key ones to avoid overcrowding)
    key_services = ['Online boarding', 'Inflight wifi service', 'Inflight entertainment', 
                   'Seat comfort', 'Ease of Online booking']
    
    for service in key_services:
        if service in service_attributes and service in plot_data.columns:
            service_data = plot_data[service].dropna()
            if len(service_data) > 0:
                dimensions.append(dict(
                    label=service, 
                    values=plot_data[service], 
                    range=[service_data.min(), service_data.max()]
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
        #title="Parallel Coordinates: Service Factors vs Satisfaction",
        height=250,
        margin=dict(l=50, r=50, t=40, b=50)
    )
    
    return fig
