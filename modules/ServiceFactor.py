import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash import html
from plotly.subplots import make_subplots
from utils import get_display_name

def create_service_factors_chart(df, service_attributes, group_col='Class', selected_subgroup=None, chart_type='average'):
    """
    Create a chart showing service factor analysis for selected subgroup
    chart_type: 'average' for average ratings, 'rf_importance' for Random Forest importance
    """
    if group_col not in df.columns or not service_attributes:
        return go.Figure().add_annotation(
            text="No data available for service factor analysis", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14)
        )
    
    # Get unique groups - preserve categorical order
    if pd.api.types.is_categorical_dtype(df[group_col]):
        groups = df[group_col].cat.categories.tolist()
    else:
        groups = df[group_col].unique().tolist()
    
    # If no specific subgroup selected, use the first one
    if selected_subgroup is None or selected_subgroup not in groups:
        selected_subgroup = groups[0] if groups else None
    
    if selected_subgroup is None:
        return go.Figure().add_annotation(
            text="No subgroup data available", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14)
        )
    
    # Filter data for selected subgroup
    subgroup_data = df[df[group_col] == selected_subgroup]
    
    if len(subgroup_data) == 0:
        return go.Figure().add_annotation(
            text=f"No data for {selected_subgroup}", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14)
        )
    
    if chart_type == 'average':
        return create_average_ratings_chart(subgroup_data, service_attributes, selected_subgroup)
    elif chart_type == 'rf_importance':
        return create_rf_importance_chart(subgroup_data, service_attributes, selected_subgroup)
    else:
        return create_combined_chart(subgroup_data, service_attributes, selected_subgroup)

def create_average_ratings_chart(subgroup_data, service_attributes, selected_subgroup):
    """
    Create horizontal bar chart showing average ratings
    """
    # Calculate average ratings for each service factor
    service_ratings = []
    service_names = []
    
    for attr in service_attributes:
        if attr in subgroup_data.columns:
            avg_rating = subgroup_data[attr].mean()
            service_ratings.append(avg_rating)
            # Use display name
            display_name = get_display_name(attr)
            service_names.append(display_name)
    
    if not service_ratings:
        return go.Figure().add_annotation(
            text="No service factor data available", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=14)
        )
    
    # Sort by rating (descending)
    sorted_data = sorted(zip(service_names, service_ratings), key=lambda x: x[1], reverse=True)
    sorted_names, sorted_ratings = zip(*sorted_data)
    
    # Create color scale based on rating values
    colors = []
    for rating in sorted_ratings:
        if rating >= 4.0:
            colors.append('#4CAF50')  # Green for high ratings
        elif rating >= 3.0:
            colors.append('#FFC107')  # Yellow for medium ratings
        elif rating >= 2.0:
            colors.append('#FF9800')  # Orange for low-medium ratings
        else:
            colors.append('#F44336')  # Red for low ratings
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=sorted_names,
            x=sorted_ratings,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(50,50,50,0.8)', width=1)
            ),
            text=[f'{rating:.2f}' for rating in sorted_ratings],
            textposition='outside',
            textfont=dict(size=10, color='black')
        )
    ])
    
    fig.update_layout(
        title={
            'text': f'Average Service Ratings - {selected_subgroup}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 14, 'color': '#1a237e'}
        },
        xaxis=dict(
            title='Average Rating',
            range=[0, 5.2],  # Slightly extend to show text
            tickvals=[0, 1, 2, 3, 4, 5],
            ticktext=['0', '1', '2', '3', '4', '5'],
            gridcolor='rgba(200,200,200,0.5)'
        ),
        yaxis=dict(
            title='Service Factors',
            automargin=True,
            tickfont=dict(size=10)
        ),
        height=350,
        margin=dict(l=20, r=40, t=40, b=40),
        plot_bgcolor='rgba(240,240,240,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig

def create_rf_importance_chart(subgroup_data, service_attributes, selected_subgroup):
    """
    Create Random Forest feature importance chart
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        # Prepare data for Random Forest
        X = subgroup_data[service_attributes].copy()
        
        # Target variable (satisfaction)
        if 'satisfaction_binary' in subgroup_data.columns:
            y = subgroup_data['satisfaction_binary']
        else:
            y = (subgroup_data['satisfaction'] == 'satisfied').astype(int)
        
        # Check if we have enough samples and both classes
        if len(subgroup_data) < 30 or len(y.unique()) < 2:
            return go.Figure().add_annotation(
                text="Insufficient data for Random Forest analysis", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            )
        
        # Train Random Forest
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        
        # Get feature importance
        importance_dict = dict(zip(service_attributes, rf.feature_importances_))
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        factors, importances = zip(*sorted_importance)
        
        # Truncate long factor names
        display_factors = [get_display_name(f) for f in factors]
        
        # Create color scale based on importance
        colors = []
        for importance in importances:
            if importance >= 0.15:
                colors.append('#FF6B6B')  # Red for very high importance
            elif importance >= 0.10:
                colors.append('#FFA726')  # Orange for high importance
            elif importance >= 0.05:
                colors.append('#FFD54F')  # Yellow for medium importance
            else:
                colors.append('#81C784')  # Green for lower importance
        
        # Calculate accuracy
        accuracy = rf.score(X_test, y_test)
        
        fig = go.Figure(data=[
            go.Bar(
                y=display_factors,
                x=importances,
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(color='rgba(50,50,50,0.8)', width=1)
                ),
                text=[f'{imp:.3f}' for imp in importances],
                textposition='outside',
                textfont=dict(size=10, color='black')
            )
        ])
        
        fig.update_layout(
            xaxis=dict(
                title='Feature Importance',
                range=[0, max(importances) * 1.15],
                gridcolor='rgba(200,200,200,0.5)',
                tickfont=dict(size=20),
                titlefont=dict(size=20)
            ),
            yaxis=dict(
                title='Service Factors',
                automargin=True,
                tickfont=dict(size=20),
                titlefont=dict(size=20)
            ),
            height=400,
            margin=dict(l=20, r=40, t=40, b=40),
            plot_bgcolor='rgba(240,240,240,0.1)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            font=dict(size=20)
        )
        fig.update_traces(textfont_size=20)
        
        return fig, accuracy
        
    except ImportError:
        return go.Figure().add_annotation(
            text="sklearn not available for Random Forest analysis", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12)
        )
    except Exception as e:
        return go.Figure().add_annotation(
            text=f"Error in Random Forest analysis: {str(e)[:50]}...", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12)
        )

def generate_service_insights(df, service_attributes, group_col='Class', selected_subgroup=None, chart_type='average'):
    """
    Generate insights text for the selected subgroup's service factors
    """
    if group_col not in df.columns or not service_attributes:
        return html.Div("No insights available", style={'color': '#666', 'fontStyle': 'italic'})
    
    # Preserve categorical order if available
    if pd.api.types.is_categorical_dtype(df[group_col]):
        groups = df[group_col].cat.categories.tolist()
    else:
        groups = df[group_col].unique().tolist()
    
    if selected_subgroup is None or selected_subgroup not in groups:
        selected_subgroup = groups[0] if groups else None
    
    if selected_subgroup is None:
        return html.Div("No subgroup selected", style={'color': '#666'})
    
    # Get subgroup data
    subgroup_data = df[df[group_col] == selected_subgroup]
    
    if len(subgroup_data) == 0:
        return html.Div(f"No data for {selected_subgroup}", style={'color': '#666'})
    
    if chart_type == 'average':
        return generate_average_insights(subgroup_data, service_attributes, selected_subgroup)
    elif chart_type == 'rf_importance':
        return generate_rf_insights(subgroup_data, service_attributes, selected_subgroup)
    else:
        return generate_combined_insights(subgroup_data, service_attributes, selected_subgroup)

def generate_average_insights(subgroup_data, service_attributes, selected_subgroup):
    """
    Generate insights for average ratings analysis
    """
    # Calculate service ratings
    service_ratings = {}
    for attr in service_attributes:
        if attr in subgroup_data.columns:
            service_ratings[attr] = subgroup_data[attr].mean()
    
    if not service_ratings:
        return html.Div("No service data available", style={'color': '#666'})
    
    # Find best and worst performing services
    best_service = max(service_ratings.items(), key=lambda x: x[1])
    worst_service = min(service_ratings.items(), key=lambda x: x[1])
    
    # Count services by performance level
    excellent_services = [name for name, rating in service_ratings.items() if rating >= 4.0]
    poor_services = [name for name, rating in service_ratings.items() if rating < 2.5]
    
    # Generate insights
    insights = []
    
    insights.append(html.P([
        html.Span("🏆 Best performing: ", style={'fontWeight': 'bold'}),
        f"{best_service[0][:30]} ({best_service[1]:.2f}/5.0)"
    ], style={'margin': '5px 0', 'fontSize': '12px'}))
    
    insights.append(html.P([
        html.Span("⚠️ Needs improvement: ", style={'fontWeight': 'bold'}),
        f"{worst_service[0][:30]} ({worst_service[1]:.2f}/5.0)"
    ], style={'margin': '5px 0', 'fontSize': '12px'}))
    
    if excellent_services:
        insights.append(html.P([
            html.Span("✅ Excellent services: ", style={'fontWeight': 'bold', 'color': '#4caf50'}),
            f"{len(excellent_services)} factors rated ≥4.0"
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
    
    if poor_services:
        insights.append(html.P([
            html.Span("🔧 Priority improvements: ", style={'fontWeight': 'bold', 'color': '#f44336'}),
            f"{len(poor_services)} factors rated <2.5"
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
    
    return html.Div(insights)

def generate_rf_insights(subgroup_data, service_attributes, selected_subgroup):
    """
    Generate insights for Random Forest importance analysis
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        # Prepare data
        X = subgroup_data[service_attributes].copy()
        
        if 'satisfaction_binary' in subgroup_data.columns:
            y = subgroup_data['satisfaction_binary']
        else:
            y = (subgroup_data['satisfaction'] == 'satisfied').astype(int)
        
        # Check data sufficiency
        if len(subgroup_data) < 30 or len(y.unique()) < 2:
            return html.Div([
                html.P("⚠️ Insufficient data for Random Forest analysis", 
                      style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'}),
                html.P(f"Need: ≥30 samples + both satisfied/dissatisfied customers", 
                      style={'color': '#666', 'fontSize': '11px'}),
                html.P(f"Current: {len(subgroup_data)} samples, {len(y.unique())} outcome types", 
                      style={'color': '#666', 'fontSize': '11px'})
            ])
        
        # Train Random Forest
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        
        # Get results
        accuracy = rf.score(X_test, y_test)
        importance_dict = dict(zip(service_attributes, rf.feature_importances_))
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Get insights
        top_factor = sorted_importance[0]
        high_importance_factors = [f for f, imp in sorted_importance if imp >= 0.10]
        low_importance_factors = [f for f, imp in sorted_importance if imp < 0.05]
        
        insights = []
        
        # Model quality
        if accuracy >= 0.85:
            model_quality = "Excellent"
            quality_color = "#4caf50"
        elif accuracy >= 0.75:
            model_quality = "Good" 
            quality_color = "#ff9800"
        else:
            model_quality = "Fair"
            quality_color = "#f44336"
        
        insights.append(html.P([
            html.Span("🤖 Model Quality: ", style={'fontWeight': 'bold'}),
            html.Span(f"{model_quality} ({accuracy:.1%} accuracy)", 
                     style={'color': quality_color, 'fontWeight': 'bold'})
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
        
        # Top driving factor
        insights.append(html.P([
            html.Span("🎯 Top Driver: ", style={'fontWeight': 'bold'}),
            f"{top_factor[0][:25]} ({top_factor[1]:.1%})"
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
        
        # High impact factors count
        insights.append(html.P([
            html.Span("⚡ High Impact: ", style={'fontWeight': 'bold', 'color': '#ff6b6b'}),
            f"{len(high_importance_factors)} factors >10% importance"
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
        
        # Strategic recommendation
        if len(high_importance_factors) <= 3:
            recommendation = "Focus on few key drivers"
            rec_color = "#4caf50"
        elif len(high_importance_factors) <= 6:
            recommendation = "Balanced multi-factor approach"
            rec_color = "#ff9800"
        else:
            recommendation = "Systematic broad improvement"
            rec_color = "#2196f3"
        
        insights.append(html.P([
            html.Span("📋 Strategy: ", style={'fontWeight': 'bold'}),
            html.Span(recommendation, style={'color': rec_color, 'fontWeight': 'bold'})
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
        
        return html.Div(insights)
        
    except ImportError:
        return html.Div("sklearn not available for Random Forest analysis", 
                       style={'color': '#f44336', 'fontStyle': 'italic', 'fontSize': '12px'})
    except Exception as e:
        return html.Div(f"RF Analysis Error: {str(e)[:50]}...", 
                       style={'color': '#f44336', 'fontStyle': 'italic', 'fontSize': '12px'})

def generate_combined_insights(subgroup_data, service_attributes, selected_subgroup):
    """
    Generate combined insights from both average ratings and RF analysis
    """
    avg_insights = generate_average_insights(subgroup_data, service_attributes, selected_subgroup)
    rf_insights = generate_rf_insights(subgroup_data, service_attributes, selected_subgroup)
    
    return html.Div([
        html.H6("📊 Rating Analysis", style={'color': '#1976d2', 'fontSize': '13px', 'marginBottom': '5px'}),
        avg_insights,
        html.Hr(style={'margin': '10px 0'}),
        html.H6("🤖 Impact Analysis", style={'color': '#7b1fa2', 'fontSize': '13px', 'marginBottom': '5px'}),
        rf_insights
    ])

def get_subgroup_comparison_data(df, service_attributes, group_col='Class'):
    """
    Get comparison data across all subgroups for context
    """
    if group_col not in df.columns or not service_attributes:
        return None
    
    comparison_data = {}
    # Preserve categorical order if available
    if pd.api.types.is_categorical_dtype(df[group_col]):
        groups = df[group_col].cat.categories.tolist()
    else:
        groups = df[group_col].unique().tolist()
    
    for group in groups:
        group_data = df[df[group_col] == group]
        group_ratings = {}
        
        for attr in service_attributes:
            if attr in group_data.columns:
                group_ratings[attr] = group_data[attr].mean()
        
        comparison_data[group] = group_ratings
    
    return comparison_data

def generate_subgroup_info_header(df, group_col='Class', selected_subgroup=None, accuracy=None):
    """
    Generate header information for the selected subgroup
    """
    if group_col not in df.columns:
        return html.Div("No subgroup data available", style={'color': '#666'})
    
    # Preserve categorical order if available
    if pd.api.types.is_categorical_dtype(df[group_col]):
        groups = df[group_col].cat.categories.tolist()
    else:
        groups = df[group_col].unique().tolist()
    
    if selected_subgroup is None or selected_subgroup not in groups:
        selected_subgroup = groups[0] if groups else None
    
    if selected_subgroup is None:
        return html.Div("No subgroup selected", style={'color': '#666'})
    
    # Get subgroup data
    subgroup_data = df[df[group_col] == selected_subgroup]
    
    if len(subgroup_data) == 0:
        return html.Div(f"No data for {selected_subgroup}", style={'color': '#666'})
    
    # Calculate metrics
    total_passengers = len(subgroup_data)
    satisfaction_rate = 0
    if 'satisfaction' in df.columns:
        satisfaction_rate = (subgroup_data['satisfaction'] == 'satisfied').mean() * 100
    
    # Calculate overall service quality score if available
    service_score = 0
    if 'Service_Quality_Score' in subgroup_data.columns:
        service_score = subgroup_data['Service_Quality_Score'].mean()
    
    # Accuracy display
    accuracy_span = None
    if accuracy is not None:
        accuracy_span = html.Span(f"Accuracy: {accuracy:.1%}", style={'fontSize': '18px', 'color': '#000', 'marginLeft': '15px'})
    
    return html.Div([
        html.H6(f"Analysis for {selected_subgroup}", 
               style={'color': '#1a237e', 'marginBottom': '8px', 'fontWeight': 'bold', 'fontSize': '20px'}),
        html.Div([
            html.Span(f"Passengers: {total_passengers:,}", 
                     style={'marginRight': '15px', 'fontSize': '18px', 'color': '#d32f2f'}),
            html.Span(f"Satisfaction: {satisfaction_rate:.1f}%", 
                     style={'marginRight': '15px', 'fontSize': '18px', 'color': '#4caf50'}),
            html.Span(f"Avg Service: {service_score:.2f}/5.0", 
                     style={'fontSize': '18px', 'color': '#2196f3'}),
            accuracy_span if accuracy_span else None
        ])
    ])