import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import html
import warnings
warnings.filterwarnings('ignore')

class SubgroupRFAnalyzer:
    """
    Random Forest analyzer to identify key service factors for each subgroup
    """
    
    def __init__(self, df, service_attributes):
        self.df = df.copy()
        self.service_attributes = service_attributes
        self.rf_models = {}
        self.feature_importance_results = {}
        self.accuracy_results = {}
        
    def prepare_data_for_subgroup(self, subgroup_data):
        """
        Prepare data for Random Forest training
        """
        # Use only service attributes as features
        X = subgroup_data[self.service_attributes].copy()
        
        # Target variable (satisfaction)
        if 'satisfaction_binary' in subgroup_data.columns:
            y = subgroup_data['satisfaction_binary']
        else:
            # Create binary satisfaction if not exists
            y = (subgroup_data['satisfaction'] == 'satisfied').astype(int)
        
        return X, y
    
    def train_rf_for_subgroup(self, subgroup_data, subgroup_name, min_samples=50):
        """
        Train Random Forest for a specific subgroup
        """
        if len(subgroup_data) < min_samples:
            print(f"Warning: {subgroup_name} has only {len(subgroup_data)} samples (min: {min_samples})")
            return None, None, None
        
        # Prepare data
        X, y = self.prepare_data_for_subgroup(subgroup_data)
        
        # Check if we have both satisfied and dissatisfied customers
        if len(y.unique()) < 2:
            print(f"Warning: {subgroup_name} has only one class (all satisfied or all dissatisfied)")
            return None, None, None
        
        # Split data
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        except ValueError:
            # If stratify fails, try without stratification
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        
        # Train Random Forest
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        rf.fit(X_train, y_train)
        
        # Calculate accuracy
        y_pred = rf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importance
        feature_importance = dict(zip(self.service_attributes, rf.feature_importances_))
        
        return rf, feature_importance, accuracy
    
    def analyze_all_subgroups(self, group_col='Class'):
        """
        Analyze all subgroups using Random Forest
        """
        print(f"=== RANDOM FOREST SUBGROUP ANALYSIS BY {group_col.upper()} ===")
        
        if group_col not in self.df.columns:
            print(f"Column {group_col} not found in dataset")
            return
        
        subgroups = sorted(self.df[group_col].unique())
        
        for subgroup in subgroups:
            subgroup_data = self.df[self.df[group_col] == subgroup]
            
            print(f"\n--- {subgroup} ---")
            print(f"Sample size: {len(subgroup_data)}")
            
            # Train Random Forest for this subgroup
            rf_model, feature_importance, accuracy = self.train_rf_for_subgroup(
                subgroup_data, subgroup
            )
            
            if rf_model is not None:
                # Store results
                self.rf_models[subgroup] = rf_model
                self.feature_importance_results[subgroup] = feature_importance
                self.accuracy_results[subgroup] = accuracy
                
                print(f"Model accuracy: {accuracy:.3f}")
                
                # Show top 5 most important factors
                sorted_importance = sorted(feature_importance.items(), 
                                         key=lambda x: x[1], reverse=True)
                print("Top 5 most impactful service factors:")
                for i, (factor, importance) in enumerate(sorted_importance[:5], 1):
                    print(f"  {i}. {factor:<30} | Importance: {importance:.4f}")
            else:
                print("Could not train model (insufficient data or no variation)")
    
    def create_feature_importance_comparison_chart(self, group_col='Class', top_n=8):
        """
        Create a comparison chart showing feature importance across subgroups
        """
        if not self.feature_importance_results:
            return go.Figure().add_annotation(
                text="No Random Forest analysis available", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14)
            )
        
        # Get all service factors
        all_factors = self.service_attributes
        subgroups = list(self.feature_importance_results.keys())
        
        # Create subplots - one for each subgroup
        fig = make_subplots(
            rows=len(subgroups), cols=1,
            subplot_titles=[f"{subgroup} (Accuracy: {self.accuracy_results.get(subgroup, 0):.2f})" 
                           for subgroup in subgroups],
            vertical_spacing=0.12
        )
        
        colors = px.colors.qualitative.Set3[:len(subgroups)]
        
        for i, subgroup in enumerate(subgroups):
            importance_dict = self.feature_importance_results[subgroup]
            
            # Sort by importance and take top N
            sorted_importance = sorted(importance_dict.items(), 
                                     key=lambda x: x[1], reverse=True)[:top_n]
            
            factors, importances = zip(*sorted_importance)
            
            # Truncate long factor names
            display_factors = [f[:20] + "..." if len(f) > 20 else f for f in factors]
            
            fig.add_trace(
                go.Bar(
                    y=display_factors,
                    x=importances,
                    orientation='h',
                    name=subgroup,
                    marker_color=colors[i],
                    text=[f'{imp:.3f}' for imp in importances],
                    textposition='outside',
                    showlegend=False
                ),
                row=i+1, col=1
            )
        
        fig.update_layout(
            title={
                'text': f'Random Forest Feature Importance by {group_col}',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1a237e'}
            },
            height=200 * len(subgroups),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        # Update x-axes
        for i in range(len(subgroups)):
            fig.update_xaxes(
                title_text="Feature Importance" if i == len(subgroups)-1 else "",
                row=i+1, col=1
            )
        
        return fig
    
    def create_single_subgroup_chart(self, selected_subgroup, group_col='Class'):
        """
        Create detailed chart for a single selected subgroup
        """
        if selected_subgroup not in self.feature_importance_results:
            return go.Figure().add_annotation(
                text=f"No Random Forest analysis for {selected_subgroup}", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14)
            )
        
        importance_dict = self.feature_importance_results[selected_subgroup]
        accuracy = self.accuracy_results[selected_subgroup]
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        factors, importances = zip(*sorted_importance)
        
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
        
        # Truncate long factor names for display
        display_factors = [f[:25] + "..." if len(f) > 25 else f for f in factors]
        
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
            title={
                'text': f'RF Feature Importance - {selected_subgroup}<br><sub>Model Accuracy: {accuracy:.2f}</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 14, 'color': '#1a237e'}
            },
            xaxis=dict(
                title='Feature Importance',
                range=[0, max(importances) * 1.15],
                gridcolor='rgba(200,200,200,0.5)'
            ),
            yaxis=dict(
                title='Service Factors',
                automargin=True,
                tickfont=dict(size=10)
            ),
            height=400,
            margin=dict(l=20, r=40, t=60, b=40),
            plot_bgcolor='rgba(240,240,240,0.1)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def generate_rf_insights(self, selected_subgroup, group_col='Class'):
        """
        Generate insights based on Random Forest analysis
        """
        if selected_subgroup not in self.feature_importance_results:
            return html.Div("No Random Forest analysis available", 
                          style={'color': '#666', 'fontStyle': 'italic'})
        
        importance_dict = self.feature_importance_results[selected_subgroup]
        accuracy = self.accuracy_results[selected_subgroup]
        
        # Sort by importance
        sorted_importance = sorted(importance_dict.items(), 
                                 key=lambda x: x[1], reverse=True)
        
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
        ], style={'margin': '5px 0'}))
        
        # Top driving factor
        insights.append(html.P([
            html.Span("🎯 Top Driver: ", style={'fontWeight': 'bold'}),
            f"{top_factor[0]} ({top_factor[1]:.1%} importance)"
        ], style={'margin': '5px 0'}))
        
        # High impact factors count
        insights.append(html.P([
            html.Span("⚡ High Impact Factors: ", style={'fontWeight': 'bold', 'color': '#ff6b6b'}),
            f"{len(high_importance_factors)} factors with >10% importance"
        ], style={'margin': '5px 0'}))
        
        # Low impact factors
        if low_importance_factors:
            insights.append(html.P([
                html.Span("💡 Optimization Opportunity: ", style={'fontWeight': 'bold', 'color': '#2196f3'}),
                f"{len(low_importance_factors)} factors have minimal impact (<5%)"
            ], style={'margin': '5px 0'}))
        
        # Strategic recommendation
        if len(high_importance_factors) <= 3:
            recommendation = "Focus resources on the few high-impact factors"
        elif len(high_importance_factors) <= 6:
            recommendation = "Balanced approach across multiple important factors"
        else:
            recommendation = "Many factors matter - systematic improvement needed"
        
        insights.append(html.P([
            html.Span("📋 Strategy: ", style={'fontWeight': 'bold', 'color': '#9c27b0'}),
            recommendation
        ], style={'margin': '5px 0'}))
        
        return html.Div(insights)
    
    def get_subgroup_rf_summary(self, group_col='Class'):
        """
        Get summary statistics for all subgroups
        """
        if not self.feature_importance_results:
            return None
        
        summary = {}
        for subgroup in self.feature_importance_results.keys():
            importance_dict = self.feature_importance_results[subgroup]
            accuracy = self.accuracy_results[subgroup]
            
            # Find top factor
            top_factor = max(importance_dict.items(), key=lambda x: x[1])
            
            # Count high impact factors
            high_impact_count = sum(1 for imp in importance_dict.values() if imp >= 0.10)
            
            summary[subgroup] = {
                'accuracy': accuracy,
                'top_factor': top_factor[0],
                'top_importance': top_factor[1],
                'high_impact_count': high_impact_count,
                'total_factors': len(importance_dict)
            }
        
        return summary

def create_rf_analysis_for_dashboard(df, service_attributes, group_col='Class', selected_subgroup=None):
    """
    Main function to create Random Forest analysis for the dashboard
    """
    # Initialize analyzer
    analyzer = SubgroupRFAnalyzer(df, service_attributes)
    
    # Run analysis for all subgroups
    analyzer.analyze_all_subgroups(group_col)
    
    # Get available subgroups
    groups = sorted(df[group_col].unique()) if group_col in df.columns else []
    
    # If no specific subgroup selected, use the first one
    if selected_subgroup is None or selected_subgroup not in groups:
        selected_subgroup = groups[0] if groups else None
    
    if selected_subgroup is None:
        return go.Figure(), html.Div("No data available")
    
    # Create chart for selected subgroup
    rf_chart = analyzer.create_single_subgroup_chart(selected_subgroup, group_col)
    
    # Generate insights
    rf_insights = analyzer.generate_rf_insights(selected_subgroup, group_col)
    
    return rf_chart, rf_insights