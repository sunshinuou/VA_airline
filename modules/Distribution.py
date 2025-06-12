import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

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
    
    # Get distribution counts
    distribution = df[group_col].value_counts()
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=distribution.index,
        values=distribution.values,
        hole=0.4,  # Creates a donut chart
        textinfo='label+percent',
        textposition='outside',
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            line=dict(color='#FFFFFF', width=2)
        )
    )])
    
    fig.update_layout(
        title={
            'text': f"{group_col} Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#1a237e', 'family': 'Arial, sans-serif'}
        },
        height=280,
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig

def analyze_service_factors_by_group(df, group_col='Class', service_attributes=None):
    """
    Analyze service factors and satisfaction rates by group
    Returns HTML content with detailed analysis
    """
    if group_col not in df.columns or service_attributes is None:
        return "Analysis not available"
    
    # Ensure we have the satisfaction column
    if 'satisfaction' not in df.columns:
        return "Satisfaction data not available"
    
    analysis_html = []
    
    # Get unique groups
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