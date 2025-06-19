import plotly.graph_objects as go
import plotly.express as px
from utils import get_display_name

def create_radar_chart(df, service_attributes, subgroup_col, subgroup_values=None):
    """
    Create interactive radar chart for service attributes by subgroup
    """
    if not service_attributes or subgroup_col not in df.columns:
        return go.Figure().add_annotation(text="No data available for radar chart", 
                                        xref="paper", yref="paper", x=0.5, y=0.5)
    
    if subgroup_values is None:
        subgroup_values = df[subgroup_col].unique()
        # limit to 4 subgroups for better readability
        if len(subgroup_values) > 4:
            subgroup_values = subgroup_values[:4]
    
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1[:len(subgroup_values)]
    
    for i, subgroup in enumerate(subgroup_values):
        subgroup_data = df[df[subgroup_col] == subgroup]
        if len(subgroup_data) == 0:
            continue
        
        # mean scores for each service attribute
        scores = [subgroup_data[attr].mean() for attr in service_attributes]
        
        display_attrs = [get_display_name(attr) for attr in service_attributes]
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],  # Close the polygon
            theta=display_attrs + [display_attrs[0]],
            fill='toself',
            name=f'{subgroup} (n={len(subgroup_data)})',
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    # Determine the scale based on actual data
    all_scores = []
    for attr in service_attributes:
        all_scores.extend(df[attr].dropna().tolist())
    
    if all_scores:
        min_score = min(all_scores)
        max_score = max(all_scores)
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[min_score, max_score],
                    tickvals=list(range(int(min_score), int(max_score)+1)),
                    ticktext=[f"{i}" for i in range(int(min_score), int(max_score)+1)],
                    tickfont=dict(size=20, family="Arial")
                ),
                angularaxis=dict(
                    tickfont=dict(size=20, family="Arial"),
                    rotation=0,
                    direction="clockwise"
                )
            ),
            showlegend=False,
            title=None,
            height=350,
            margin=dict(l=20, r=40, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            uirevision='constant',
            font=dict(size=20, family="Arial")
        )
    
    return fig
