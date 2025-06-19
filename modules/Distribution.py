import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import get_display_value

def create_distribution_chart(df, group_col='Class'):
    """
    Create a pie chart for distribution analysis
    """
    if group_col not in df.columns:
        # Fallback to a simple message if column doesn't exist
        fig = go.Figure()
        fig.add_annotation(
            text=f"Column '{group_col}' not found in dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Distribution Chart",
            height=300,
            showlegend=False
        )
        return fig
    
    # Get distribution counts - preserve categorical order
    if pd.api.types.is_categorical_dtype(df[group_col]):
        # For categorical data, use the categories in their defined order
        categories = df[group_col].cat.categories
        distribution = df[group_col].value_counts().reindex(categories)
    else:
        # For non-categorical data, use natural order (don't sort alphabetically)
        distribution = df[group_col].value_counts(sort=False)
    
    # Map labels for display
    display_labels = [get_display_value(val) for val in distribution.index]
    
    # Get colors from the same palette as radar chart and make them more transparent
    base_colors = px.colors.qualitative.Set1[:len(distribution)]
    colors = [c.replace('rgb', 'rgba').replace(')', ',0.7)') for c in base_colors]
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=display_labels,
        values=distribution.values,
        hole=0.4,  # Creates a donut chart
        textinfo='percent',  # Only show percent
        textposition='outside',
        marker=dict(
            colors=colors,
            line=dict(color='#FFFFFF', width=2)
        ),
        sort=False
    )])
    
    fig.update_layout(
        title={
            'text': 'Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'color': '#1a237e', 'family': 'Arial, sans-serif'}
        },
        height=400,
        margin=dict(t=40, b=80, l=20, r=20),
        font=dict(size=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            font=dict(size=20),
            x=0.5,
            y=-0.1,
            xanchor='center',
            yanchor='top'
        )
    )
    fig.update_traces(textfont_size=16, marker=dict(line=dict(width=3)))
    
    return fig

def analyze_service_factors_by_group(df, group_col='Class', service_attributes=None):
    """
    Analyze service factors and satisfaction rates by group
    Returns HTML content with detailed analysis
    """
    if group_col not in df.columns or service_attributes is None:
        return "Analysis not available"
    if 'satisfaction' not in df.columns:
        return "Satisfaction data not available"
    
    analysis_html = []
    
    # get unique groups
    groups = df[group_col].unique()
    
    for group in sorted(groups):
        group_data = df[df[group_col] == group]
        
        # Calculate satisfaction rate
        satisfaction_rate = (group_data['satisfaction'] == 'satisfied').mean() * 100
        
        # Calculate average ratings for service attributes
        service_ratings = {}
        for attr in service_attributes:
            if attr in group_data.columns:
                avg_rating = group_data[attr].mean()
                service_ratings[attr] = avg_rating
        
        # Sort by average rating (descending)
        top_services = sorted(service_ratings.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Create HTML for this group
        group_html = f"""
        <div style="margin-bottom: 25px; padding: 15px; border-left: 4px solid #1a237e; background-color: #f8f9fa;">
            <h6 style="color: #1a237e; font-weight: bold; margin-bottom: 10px;">--- {group} ---</h6>
            <p style="margin-bottom: 10px; font-weight: bold;">
                Satisfaction Rate: <span style="color: #4caf50;">{satisfaction_rate:.1f}%</span>
            </p>
            <p style="margin-bottom: 8px; font-weight: bold;">Top service factors (by average rating):</p>
            <div style="margin-left: 15px;">
        """
        
        for i, (service, rating) in enumerate(top_services, 1):
            # Truncate long service names for better display
            display_name = service if len(service) <= 25 else service[:22] + "..."
            group_html += f"""
                <p style="margin: 3px 0; font-size: 13px; font-family: monospace;">
                    {i}. {display_name:<25} | Avg Rating: <span style="color: #2196f3; font-weight: bold;">{rating:.2f}</span>
                </p>
            """
        
        group_html += """
            </div>
        </div>
        """
        
        analysis_html.append(group_html)
    
    return "".join(analysis_html)