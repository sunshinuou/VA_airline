import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import html
import warnings
warnings.filterwarnings('ignore')

class SHAPAnalyzer:
    """
    SHAP analyzer for feature importance and explanation
    """
    
    def __init__(self, df, service_attributes):
        self.df = df.copy()
        self.service_attributes = service_attributes
        self.shap_values = {}
        self.models = {}
        self.explainers = {}
        
    def prepare_data_for_subgroup(self, subgroup_data):
        """
        Prepare data for SHAP analysis
        """
        # Use only service attributes as features
        X = subgroup_data[self.service_attributes].copy()
        
        # Target variable (satisfaction)
        if 'satisfaction_binary' in subgroup_data.columns:
            y = subgroup_data['satisfaction_binary']
        else:
            y = (subgroup_data['satisfaction'] == 'satisfied').astype(int)
        
        return X, y
    
    def train_model_and_calculate_shap(self, subgroup_data, subgroup_name, min_samples=50):
        """
        Train model and calculate SHAP values for a specific subgroup
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            import shap
        except ImportError:
            print("Required libraries (sklearn, shap) not available")
            return None, None, None, None
        
        if len(subgroup_data) < min_samples:
            return None, None, None, None
        
        # Prepare data
        X, y = self.prepare_data_for_subgroup(subgroup_data)
        
        # Check if we have both satisfied and dissatisfied customers
        if len(y.unique()) < 2:
            return None, None, None, None
        
        # Check if X is empty or has no features
        if X.empty or len(self.service_attributes) == 0:
            return None, None, None, None
        
        # Split data
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        except ValueError:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        
        try:
            # Train Random Forest
            rf = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            rf.fit(X_train, y_train)
            
            # Calculate SHAP values
            explainer = shap.TreeExplainer(rf)
            shap_values = explainer.shap_values(X_test)
            
            # FIXED: Handle binary classification SHAP output properly
            # For binary classification, SHAP returns either:
            # 1. A list of 2 arrays (one for each class)
            # 2. A single array for the positive class
            # 3. Sometimes concatenated arrays
            
            if isinstance(shap_values, list):
                if len(shap_values) == 2:
                    # Take positive class (index 1)
                    shap_values = shap_values[1]
                elif len(shap_values) == 1:
                    shap_values = shap_values[0]
            
            # Ensure proper shape - should be (n_samples, n_features)
            if isinstance(shap_values, np.ndarray):
                if shap_values.ndim == 1:
                    shap_values = shap_values.reshape(1, -1)
                
                # Check if we have the wrong number of features (doubled for binary classification)
                expected_features = len(self.service_attributes)
                if shap_values.shape[1] == expected_features * 2:
                    # Take only the first half (positive class features)
                    shap_values = shap_values[:, :expected_features]
                elif shap_values.shape[1] != expected_features:
                    print(f"Warning: SHAP values shape {shap_values.shape} doesn't match expected features {expected_features}")
            
            # Calculate accuracy
            accuracy = rf.score(X_test, y_test)
            
            return shap_values, explainer, accuracy, X_test
            
        except Exception as e:
            print(f"Error in SHAP calculation: {e}")
            return None, None, None, None
    
    def analyze_subgroup_shap(self, group_col='Class', selected_subgroup=None):
        """
        Analyze SHAP values for a specific subgroup
        """
        if group_col not in self.df.columns:
            return None
        
        groups = sorted(self.df[group_col].unique())
        
        if selected_subgroup is None or selected_subgroup not in groups:
            selected_subgroup = groups[0] if groups else None
        
        if selected_subgroup is None:
            return None
        
        # Filter data for selected subgroup
        subgroup_data = self.df[self.df[group_col] == selected_subgroup]
        
        # Train model and calculate SHAP
        result = self.train_model_and_calculate_shap(subgroup_data, selected_subgroup)
        
        if len(result) != 4 or result[0] is None:
            return None
        
        shap_values, explainer, accuracy, X_test = result
        
        # Store results
        self.shap_values[selected_subgroup] = shap_values
        self.explainers[selected_subgroup] = explainer
        
        return {
            'subgroup': selected_subgroup,
            'shap_values': shap_values,
            'explainer': explainer,
            'accuracy': accuracy,
            'X_test': X_test
        }
    
    def create_shap_summary_chart(self, group_col='Class', selected_subgroup=None):
        """
        Create SHAP summary chart (mean absolute SHAP values)
        """
        shap_result = self.analyze_subgroup_shap(group_col, selected_subgroup)
        
        if shap_result is None:
            return go.Figure().add_annotation(
                text="No SHAP analysis available\n(insufficient data or missing libraries)", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            )
        
        shap_values = shap_result['shap_values']
        accuracy = shap_result['accuracy']
        subgroup = shap_result['subgroup']
        
        try:
            # Calculate mean absolute SHAP values for each feature - ULTRA SAFE VERSION
            if isinstance(shap_values, list):
                shap_values = np.array(shap_values)
            
            # Handle different array shapes and binary classification
            if shap_values.ndim == 0:
                shap_values = shap_values.reshape(1, 1)
            elif shap_values.ndim == 1:
                shap_values = shap_values.reshape(1, -1)
            
            # CRITICAL: Handle binary classification feature doubling
            expected_features = len(self.service_attributes)
            if len(shap_values.shape) >= 2 and shap_values.shape[1] == expected_features * 2:
                shap_values = shap_values[:, :expected_features]
            
            try:
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
                mean_abs_shap = mean_abs_shap.flatten()  # Ensure 1D
            except Exception:
                return go.Figure().add_annotation(
                    text="Error calculating SHAP means", 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=12)
                )
            
            # Use only the features we can match
            min_features = min(len(self.service_attributes), len(mean_abs_shap))
            service_attrs_subset = self.service_attributes[:min_features]
            mean_abs_shap = mean_abs_shap[:min_features]
            
            # Create feature importance ranking with safe conversion
            feature_importance = {}
            for i, attr in enumerate(service_attrs_subset):
                if i < len(mean_abs_shap):
                    try:
                        val = mean_abs_shap[i]
                        if hasattr(val, 'item'):  # numpy scalar
                            feature_importance[attr] = val.item()
                        else:
                            feature_importance[attr] = float(val)
                    except (ValueError, TypeError):
                        continue
            
            # Check if feature_importance is empty
            if not feature_importance:
                return go.Figure().add_annotation(
                    text="No feature importance data available", 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=12)
                )
            
            try:
                sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            except Exception:
                return go.Figure().add_annotation(
                    text="Error sorting features", 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=12)
                )
            
            factors, importances = zip(*sorted_importance) if sorted_importance else ([], [])
            
            # Check if we have any factors to display
            if not factors:
                return go.Figure().add_annotation(
                    text="No factors available for SHAP analysis", 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=12)
                )
            
            # Create color scale based on SHAP importance
            colors = []
            for importance in importances:
                max_importance = max(importances) if importances else 1
                normalized_importance = importance / max_importance
                
                if normalized_importance >= 0.8:
                    colors.append('#FF6B6B')  # Red for very high importance
                elif normalized_importance >= 0.6:
                    colors.append('#FFA726')  # Orange for high importance
                elif normalized_importance >= 0.4:
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
                    'text': f'SHAP Feature Importance - {subgroup}<br><sub>Model Accuracy: {accuracy:.1%}</sub>',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 14, 'color': '#1a237e'}
                },
                xaxis=dict(
                    title='Mean |SHAP Value|',
                    range=[0, max(importances) * 1.15 if importances else 1],
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
            
        except Exception as e:
            return go.Figure().add_annotation(
                text=f"Error creating SHAP chart: {str(e)[:50]}...", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            )
    
    def create_shap_waterfall_chart(self, group_col='Class', selected_subgroup=None, sample_index=0):
        """
        Create SHAP waterfall chart for a single prediction - ULTRA ROBUST VERSION
        """
        shap_result = self.analyze_subgroup_shap(group_col, selected_subgroup)
        
        if shap_result is None:
            return go.Figure().add_annotation(
                text="No SHAP analysis available", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            )
        
        try:
            shap_values = shap_result['shap_values']
            X_test = shap_result['X_test']
            subgroup = shap_result['subgroup']
            
            # ROBUST: Handle different SHAP array formats
            if isinstance(shap_values, list):
                if len(shap_values) == 2:
                    shap_values = np.array(shap_values[1])  # Take positive class
                elif len(shap_values) == 1:
                    shap_values = np.array(shap_values[0])
                else:
                    shap_values = np.array(shap_values)
            
            # Ensure proper shape
            if shap_values.ndim == 1:
                shap_values = shap_values.reshape(1, -1)
            
            # Handle binary classification feature doubling
            expected_features = len(self.service_attributes)
            if shap_values.shape[1] == expected_features * 2:
                shap_values = shap_values[:, :expected_features]
            
            # Ensure sample_index is valid
            if sample_index >= len(shap_values):
                sample_index = 0
            
            # Get SHAP values for selected sample
            sample_shap = shap_values[sample_index]
            sample_features = X_test.iloc[sample_index]
            
            # Ensure we're working with the right number of features
            min_features = min(len(self.service_attributes), len(sample_shap))
            service_attrs_subset = self.service_attributes[:min_features]
            sample_shap = sample_shap[:min_features]
            
            print(f"Waterfall debug: {len(self.service_attributes)} service attrs, {len(sample_shap)} SHAP values, using {min_features}")
            print(f"Sample SHAP range: {sample_shap.min():.6f} to {sample_shap.max():.6f}")
            print(f"Sample SHAP non-zero count: {np.count_nonzero(np.abs(sample_shap) > 1e-6)}")
            
            # Get base value (expected value) with safe handling
            try:
                explainer = shap_result['explainer']
                base_value = explainer.expected_value
                if isinstance(base_value, np.ndarray):
                    if len(base_value) > 1:
                        base_value = float(base_value[1])  # Positive class for binary
                    else:
                        base_value = float(base_value[0])
                elif hasattr(base_value, 'item'):
                    base_value = base_value.item()
                else:
                    base_value = float(base_value)
            except Exception:
                base_value = 0.5  # Default for binary classification
            
            # Create waterfall data with safe conversion
            feature_contributions = []
            for i, attr in enumerate(service_attrs_subset):
                try:
                    if i < len(sample_shap):
                        shap_val = sample_shap[i]
                        if hasattr(shap_val, 'item'):
                            shap_val = shap_val.item()
                        else:
                            shap_val = float(shap_val)
                        
                        # Get feature value safely
                        if i < len(sample_features):
                            feature_val = sample_features.iloc[i]
                        else:
                            feature_val = 0
                        
                        # Include all contributions regardless of size for waterfall
                        feature_contributions.append((attr, shap_val, feature_val))
                            
                except (ValueError, TypeError, IndexError) as e:
                    print(f"Error processing feature {i} ({attr if i < len(service_attrs_subset) else 'unknown'}): {e}")
                    continue
            
            print(f"Generated {len(feature_contributions)} feature contributions")
            
            # If still no contributions found, provide debug info
            if not feature_contributions:
                debug_info = f"Debug Info:\n"
                debug_info += f"- Service attributes: {len(service_attrs_subset)}\n"
                debug_info += f"- Sample SHAP length: {len(sample_shap)}\n"
                debug_info += f"- Sample features length: {len(sample_features)}\n"
                debug_info += f"- SHAP values sample: {sample_shap[:3] if len(sample_shap) > 0 else 'None'}"
                
                return go.Figure().add_annotation(
                    text=debug_info, 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=10)
                )
            
            # Sort by absolute SHAP value
            feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            
            # Take top 8 features for better visualization
            top_features = feature_contributions[:8]
            
            print(f"Top features: {[(f, round(v, 4)) for f, v, _ in top_features[:3]]}")
            
            if not top_features:
                return go.Figure().add_annotation(
                    text="No feature contributions available after filtering", 
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=12)
                )
            
            # Prepare waterfall chart data
            labels = ['Base'] + [f[:15] for f, _, _ in top_features] + ['Prediction']
            values = [base_value]
            colors = ['blue']
            
            cumulative = base_value
            for feature, shap_val, feature_val in top_features:
                values.append(shap_val)
                cumulative += shap_val
                colors.append('green' if shap_val > 0 else 'red')
            
            values.append(cumulative)
            colors.append('blue')
            
            # Create the waterfall chart
            fig = go.Figure()
            
            # Calculate positions for waterfall effect
            running_total = 0
            
            for i, (label, value, color) in enumerate(zip(labels, values, colors)):
                if i == 0:
                    # Base value
                    fig.add_trace(go.Bar(
                        x=[label],
                        y=[value],
                        name=label,
                        marker_color=color,
                        showlegend=False,
                        text=f'{value:.3f}',
                        textposition='middle center',
                        textfont=dict(color='white', size=10)
                    ))
                    running_total = value
                elif i == len(labels) - 1:
                    # Final prediction
                    fig.add_trace(go.Bar(
                        x=[label],
                        y=[value],
                        name=label,
                        marker_color=color,
                        showlegend=False,
                        text=f'{value:.3f}',
                        textposition='middle center',
                        textfont=dict(color='white', size=10)
                    ))
                else:
                    # SHAP contribution
                    if value >= 0:
                        # Positive contribution
                        fig.add_trace(go.Bar(
                            x=[label],
                            y=[value],
                            base=running_total,
                            name=label,
                            marker_color=color,
                            showlegend=False,
                            text=f'+{value:.3f}',
                            textposition='middle center',
                            textfont=dict(color='white', size=9)
                        ))
                    else:
                        # Negative contribution
                        fig.add_trace(go.Bar(
                            x=[label],
                            y=[abs(value)],
                            base=running_total + value,
                            name=label,
                            marker_color=color,
                            showlegend=False,
                            text=f'{value:.3f}',
                            textposition='middle center',
                            textfont=dict(color='white', size=9)
                        ))
                    
                    running_total += value
            
            fig.update_layout(
                title={
                    'text': f'SHAP Explanation - {subgroup} (Sample #{sample_index + 1})',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 14, 'color': '#1a237e'}
                },
                xaxis=dict(
                    title='Features',
                    tickangle=45
                ),
                yaxis=dict(title='SHAP Value'),
                height=400,
                margin=dict(l=20, r=20, t=60, b=80),
                plot_bgcolor='rgba(240,240,240,0.1)',
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            return go.Figure().add_annotation(
                text=f"Error creating waterfall chart: {str(e)[:50]}...", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            )
    
    def generate_shap_insights(self, group_col='Class', selected_subgroup=None):
        """
        Generate insights based on SHAP analysis - ULTRA ROBUST VERSION
        """
        shap_result = self.analyze_subgroup_shap(group_col, selected_subgroup)
        
        if shap_result is None:
            return html.Div([
                html.P("⚠️ SHAP analysis not available", 
                      style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'}),
                html.P("Requires: sklearn, shap libraries + sufficient data", 
                      style={'color': '#666', 'fontSize': '11px'})
            ])
        
        try:
            shap_values = shap_result['shap_values']
            accuracy = shap_result['accuracy']
            subgroup = shap_result['subgroup']
            
            # ULTRA ROBUST: Handle various SHAP array formats
            if isinstance(shap_values, list):
                if len(shap_values) == 2:
                    # Binary classification - take positive class
                    shap_values = np.array(shap_values[1])
                elif len(shap_values) == 1:
                    shap_values = np.array(shap_values[0])
                else:
                    shap_values = np.array(shap_values)
            
            # Ensure it's at least 1D
            if shap_values.ndim == 0:
                shap_values = shap_values.reshape(1, 1)
            elif shap_values.ndim == 1:
                shap_values = shap_values.reshape(1, -1)
            
            # CRITICAL FIX: Handle doubled features from binary classification
            expected_features = len(self.service_attributes)
            actual_shape = shap_values.shape
            
            if len(actual_shape) >= 2:
                actual_features = actual_shape[1]
                
                # If we have exactly double the features, take the first half
                if actual_features == expected_features * 2:
                    shap_values = shap_values[:, :expected_features]
                    print(f"Fixed binary classification: reduced from {actual_features} to {expected_features} features")
                # If we have some other mismatch, try to handle it
                elif actual_features != expected_features:
                    print(f"Warning: Feature count mismatch - expected {expected_features}, got {actual_features}")
                    # Try to take the first N features if we have more than expected
                    if actual_features > expected_features:
                        shap_values = shap_values[:, :expected_features]
                    else:
                        return html.Div([
                            html.P(f"⚠️ Cannot fix feature mismatch: expected {expected_features}, got {actual_features}", 
                                  style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
                        ])
            
            # Calculate feature insights with ultra-safe array handling
            try:
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
                # Flatten in case it's still multi-dimensional
                mean_abs_shap = mean_abs_shap.flatten()
            except Exception as e:
                return html.Div([
                    html.P(f"⚠️ Error calculating SHAP means: {str(e)[:30]}...", 
                          style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
                ])
            
            # Ensure we have the right number of features
            expected_features = len(self.service_attributes)
            actual_features = len(mean_abs_shap)
            
            # Don't error out - just report the issue and try to proceed
            if actual_features != expected_features:
                print(f"Feature count after processing: expected {expected_features}, got {actual_features}")
                # Try to align by taking minimum
                min_features = min(expected_features, actual_features)
                service_attrs_subset = self.service_attributes[:min_features]
                mean_abs_shap = mean_abs_shap[:min_features]
            else:
                service_attrs_subset = self.service_attributes
            
            # ULTRA SAFE: Convert each value individually with error handling
            feature_importance = {}
            for i, attr in enumerate(service_attrs_subset):
                try:
                    if i < len(mean_abs_shap):
                        # Handle various numpy types
                        val = mean_abs_shap[i]
                        if hasattr(val, 'item'):  # numpy scalar
                            feature_importance[attr] = val.item()
                        else:
                            feature_importance[attr] = float(val)
                except (ValueError, TypeError, IndexError) as e:
                    # Skip problematic values
                    continue
            
            # Check if we got any valid features
            if not feature_importance:
                return html.Div([
                    html.P("⚠️ No valid feature importance values", 
                          style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
                ])
            
            # Safe sorting
            try:
                sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            except Exception as e:
                return html.Div([
                    html.P(f"⚠️ Error sorting features: {str(e)[:30]}...", 
                          style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
                ])
            
            if not sorted_importance:
                return html.Div([
                    html.P("⚠️ No features to display", 
                          style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
                ])
            
            top_factor = sorted_importance[0]
            
            # Safe threshold calculation
            try:
                importance_values = [imp for _, imp in sorted_importance]
                threshold_70th = np.percentile(importance_values, 70)
                high_impact_factors = [f for f, imp in sorted_importance if imp >= threshold_70th]
            except Exception:
                high_impact_factors = sorted_importance[:3]  # Fallback to top 3
            
            # Calculate directional impact with extra safety
            positive_factors = []
            negative_factors = []
            
            try:
                mean_shap = shap_values.mean(axis=0)
                mean_shap = mean_shap.flatten()  # Ensure 1D
                
                for i, attr in enumerate(service_attrs_subset):
                    if i < len(mean_shap):
                        try:
                            val = mean_shap[i]
                            if hasattr(val, 'item'):
                                shap_val = val.item()
                            else:
                                shap_val = float(val)
                            
                            if shap_val > 0:
                                positive_factors.append(attr)
                            elif shap_val < 0:
                                negative_factors.append(attr)
                        except (ValueError, TypeError):
                            continue
            except Exception:
                # If directional analysis fails, provide basic info
                positive_factors = ["Analysis incomplete"]
                negative_factors = ["Analysis incomplete"]
            
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
                html.Span("🤖 SHAP Model: ", style={'fontWeight': 'bold'}),
                html.Span(f"{model_quality} ({accuracy:.1%} accuracy)", 
                         style={'color': quality_color, 'fontWeight': 'bold'})
            ], style={'margin': '5px 0', 'fontSize': '12px'}))
            
            # Top explanatory factor
            insights.append(html.P([
                html.Span("🎯 Most Explanatory: ", style={'fontWeight': 'bold'}),
                f"{top_factor[0][:25]} (|SHAP|: {top_factor[1]:.3f})"
            ], style={'margin': '5px 0', 'fontSize': '12px'}))
            
            # Directional impact
            insights.append(html.P([
                html.Span("📈 Positive Impact: ", style={'fontWeight': 'bold', 'color': '#4caf50'}),
                f"{len(positive_factors)} factors boost satisfaction"
            ], style={'margin': '5px 0', 'fontSize': '12px'}))
            
            insights.append(html.P([
                html.Span("📉 Negative Impact: ", style={'fontWeight': 'bold', 'color': '#f44336'}),
                f"{len(negative_factors)} factors reduce satisfaction"
            ], style={'margin': '5px 0', 'fontSize': '12px'}))
            
            # Strategic insight
            if len(high_impact_factors) <= 3:
                strategy = "Focus on few key explainable factors"
            elif len(high_impact_factors) <= 6:
                strategy = "Multi-factor explainable approach"
            else:
                strategy = "Complex interaction patterns detected"
            
            insights.append(html.P([
                html.Span("💡 SHAP Strategy: ", style={'fontWeight': 'bold', 'color': '#9c27b0'}),
                strategy
            ], style={'margin': '5px 0', 'fontSize': '12px'}))
            
            return html.Div(insights)
            
        except Exception as e:
            return html.Div([
                html.P(f"⚠️ Error generating insights: {str(e)[:50]}...", 
                      style={'color': '#ff9800', 'fontWeight': 'bold', 'fontSize': '12px'})
            ])

def create_shap_analysis_for_dashboard(df, service_attributes, group_col='Class', selected_subgroup=None, chart_type='summary'):
    """
    Main function to create SHAP analysis for the dashboard
    """
    try:
        # Initialize analyzer
        analyzer = SHAPAnalyzer(df, service_attributes)
        
        # Get available subgroups
        groups = sorted(df[group_col].unique()) if group_col in df.columns else []
        
        # If no specific subgroup selected, use the first one
        if selected_subgroup is None or selected_subgroup not in groups:
            selected_subgroup = groups[0] if groups else None
        
        if selected_subgroup is None:
            return go.Figure().add_annotation(
                text="No data available", 
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=12)
            ), html.Div("No data available")
        
        # Create chart based on type
        if chart_type == 'summary':
            shap_chart = analyzer.create_shap_summary_chart(group_col, selected_subgroup)
        elif chart_type == 'waterfall':
            shap_chart = analyzer.create_shap_waterfall_chart(group_col, selected_subgroup)
        else:
            shap_chart = analyzer.create_shap_summary_chart(group_col, selected_subgroup)
        
        # Generate insights
        shap_insights = analyzer.generate_shap_insights(group_col, selected_subgroup)
        
        return shap_chart, shap_insights
        
    except Exception as e:
        error_fig = go.Figure().add_annotation(
            text=f"Error in SHAP analysis: {str(e)[:50]}...", 
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=12)
        )
        error_insights = html.Div([
            html.P(f"⚠️ SHAP Error: {str(e)[:100]}...", 
                  style={'color': '#f44336', 'fontWeight': 'bold', 'fontSize': '12px'})
        ])
        return error_fig, error_insights