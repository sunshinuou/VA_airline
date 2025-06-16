import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import html, dcc
import warnings
warnings.filterwarnings('ignore')

class PassengerSegmentationAnalyzer:
    """
    Advanced clustering analysis for passenger segmentation
    """
    
    def __init__(self, df, service_attributes):
        self.df = df.copy()
        self.service_attributes = service_attributes
        self.scaled_features = None
        self.cluster_results = {}
        self.pca_components = None
        self.feature_encoders = {}
        
    def prepare_clustering_features(self, include_categorical=True):
        """
        Prepare features for clustering analysis
        """
        clustering_features = []
        
        # Service attributes (numerical)
        clustering_features.extend(self.service_attributes)
        
        # Additional numerical features
        numerical_features = [
            'Age', 'Flight Distance', 
            'Departure Delay in Minutes', 'Arrival Delay in Minutes'
        ]
        
        for feature in numerical_features:
            if feature in self.df.columns:
                clustering_features.append(feature)
        
        # Categorical features (if requested)
        if include_categorical:
            categorical_features = [
                'Gender', 'Customer Type', 'Type of Travel', 'Class'
            ]
            
            for feature in categorical_features:
                if feature in self.df.columns:
                    # Encode categorical variables
                    le = LabelEncoder()
                    encoded_col = f'{feature}_encoded'
                    self.df[encoded_col] = le.fit_transform(self.df[feature].astype(str))
                    clustering_features.append(encoded_col)
                    self.feature_encoders[feature] = le
        
        # Prepare feature matrix
        X = self.df[clustering_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        scaler = StandardScaler()
        self.scaled_features = scaler.fit_transform(X)
        
        return clustering_features, self.scaled_features
    
    def find_optimal_clusters(self, max_clusters=8):
        """
        Find optimal number of clusters using multiple metrics
        """
        _, X_scaled = self.prepare_clustering_features()
        
        cluster_range = range(2, max_clusters + 1)
        inertias = []
        silhouette_scores = []
        calinski_scores = []
        
        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
            calinski_scores.append(calinski_harabasz_score(X_scaled, cluster_labels))
        
        # Find optimal clusters (highest silhouette score)
        optimal_k = cluster_range[np.argmax(silhouette_scores)]
        
        return {
            'cluster_range': list(cluster_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'calinski_scores': calinski_scores,
            'optimal_k': optimal_k
        }
    
    def perform_kmeans_clustering(self, n_clusters=None):
        """
        Perform K-means clustering
        """
        features, X_scaled = self.prepare_clustering_features()
        
        if n_clusters is None:
            optimal_results = self.find_optimal_clusters()
            n_clusters = optimal_results['optimal_k']
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to dataframe
        self.df['Cluster'] = cluster_labels
        
        # Calculate cluster centers in original space
        cluster_centers = []
        for i in range(n_clusters):
            cluster_data = self.df[self.df['Cluster'] == i]
            center = {}
            for feature in self.service_attributes:
                center[feature] = cluster_data[feature].mean()
            cluster_centers.append(center)
        
        # Store results
        self.cluster_results['kmeans'] = {
            'model': kmeans,
            'n_clusters': n_clusters,
            'labels': cluster_labels,
            'centers': cluster_centers,
            'silhouette_score': silhouette_score(X_scaled, cluster_labels)
        }
        
        return cluster_labels
    
    def perform_pca_analysis(self, n_components=2):
        """
        Perform PCA for dimensionality reduction and visualization
        """
        features, X_scaled = self.prepare_clustering_features()
        
        pca = PCA(n_components=n_components)
        self.pca_components = pca.fit_transform(X_scaled)
        
        # Store feature contributions to principal components
        self.pca_feature_contributions = {}
        for i in range(n_components):
            component_contributions = dict(zip(self.service_attributes, pca.components_[i]))
            # Sort by absolute contribution
            sorted_contributions = sorted(component_contributions.items(), 
                                       key=lambda x: abs(x[1]), 
                                       reverse=True)
            self.pca_feature_contributions[f'PC{i+1}'] = sorted_contributions
        
        # Add PCA components to dataframe
        for i in range(n_components):
            self.df[f'PCA_{i+1}'] = self.pca_components[:, i]
        
        return pca, self.pca_components
    
    def analyze_cluster_characteristics(self):
        """
        Analyze characteristics of each cluster
        """
        if 'Cluster' not in self.df.columns:
            self.perform_kmeans_clustering()
        
        cluster_analysis = {}
        n_clusters = self.df['Cluster'].nunique()
        
        for cluster_id in range(n_clusters):
            cluster_data = self.df[self.df['Cluster'] == cluster_id]
            
            # Basic statistics
            analysis = {
                'size': len(cluster_data),
                'size_percentage': len(cluster_data) / len(self.df) * 100,
                'satisfaction_rate': (cluster_data['satisfaction'] == 'satisfied').mean() * 100,
                'avg_service_scores': {},
                'dominant_characteristics': {}
            }
            
            # Service scores
            for attr in self.service_attributes:
                analysis['avg_service_scores'][attr] = cluster_data[attr].mean()
            
            # Dominant characteristics
            categorical_features = ['Gender', 'Customer Type', 'Type of Travel', 'Class']
            for feature in categorical_features:
                if feature in cluster_data.columns:
                    mode_value = cluster_data[feature].mode()
                    if len(mode_value) > 0:
                        analysis['dominant_characteristics'][feature] = mode_value[0]
            
            # Age statistics
            if 'Age' in cluster_data.columns:
                analysis['avg_age'] = cluster_data['Age'].mean()
                analysis['age_range'] = f"{cluster_data['Age'].min()}-{cluster_data['Age'].max()}"
            
            cluster_analysis[cluster_id] = analysis
        
        return cluster_analysis
    
    def create_cluster_visualization(self, chart_type='pca_scatter'):
        """
        Create various cluster visualization charts
        """
        if chart_type == 'pca_scatter':
            return self.create_pca_scatter_plot()
        elif chart_type == 'cluster_comparison':
            return self.create_cluster_comparison_chart()
        elif chart_type == 'cluster_profiles':
            return self.create_cluster_profiles_chart()
        else:
            return self.create_pca_scatter_plot()  # Default to PCA scatter plot
    
    def create_pca_scatter_plot(self):
        """
        Create PCA scatter plot with cluster colors
        """
        if self.pca_components is None:
            self.perform_pca_analysis()
        
        # Create scatter plot
        fig = go.Figure()
        
        n_clusters = self.df['Cluster'].nunique()
        colors = px.colors.qualitative.Set3[:n_clusters]
        
        for cluster_id in range(n_clusters):
            cluster_data = self.df[self.df['Cluster'] == cluster_id]
            
            fig.add_trace(go.Scatter(
                x=cluster_data['PCA_1'],
                y=cluster_data['PCA_2'],
                mode='markers',
                marker=dict(
                    color=colors[cluster_id],
                    size=6,
                    opacity=0.7,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name=f'Cluster {cluster_id}',
                text=[f'Satisfaction: {sat}<br>Service Score: {score:.2f}' 
                      for sat, score in zip(cluster_data['satisfaction'], 
                                          cluster_data['Service_Quality_Score'])],
                hovertemplate='<b>%{fullData.name}</b><br>' +
                            'PCA 1: %{x:.2f}<br>' +
                            'PCA 2: %{y:.2f}<br>' +
                            '%{text}<extra></extra>'
            ))
        
        # Get top features for each principal component
        pc1_top_features = [f"{f[:20]}..." if len(f) > 20 else f for f, _ in self.pca_feature_contributions['PC1'][:3]]
        pc2_top_features = [f"{f[:20]}..." if len(f) > 20 else f for f, _ in self.pca_feature_contributions['PC2'][:3]]
        
        pc1_title = f"First Principal Component<br><sub>Top features: {', '.join(pc1_top_features)}</sub>"
        pc2_title = f"Second Principal Component<br><sub>Top features: {', '.join(pc2_top_features)}</sub>"
        
        fig.update_layout(
            title={
                'text': 'Passenger Segments (PCA Visualization)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1a237e'}
            },
            xaxis_title=pc1_title,
            yaxis_title=pc2_title,
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            showlegend=True
        )
        
        return fig
    
    def create_cluster_profiles_chart(self):
        """
        Create radar chart showing service profiles for each cluster
        """
        if 'Cluster' not in self.df.columns:
            self.perform_kmeans_clustering()
        
        # Calculate mean service scores for each cluster
        cluster_profiles = []
        for cluster_id in sorted(self.df['Cluster'].unique()):
            cluster_data = self.df[self.df['Cluster'] == cluster_id]
            profile = {
                'Cluster': f'Cluster {cluster_id}',
                'Size': len(cluster_data),
                'Satisfaction': (cluster_data['satisfaction'] == 'satisfied').mean() * 100
            }
            
            # Add service scores
            for attr in self.service_attributes:
                profile[attr] = cluster_data[attr].mean()
            
            cluster_profiles.append(profile)
        
        # Create radar chart
        fig = go.Figure()
        
        for profile in cluster_profiles:
            cluster_name = profile['Cluster']
            values = [profile[attr] for attr in self.service_attributes]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=self.service_attributes,
                name=cluster_name,
                fill='toself'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )
            ),
            showlegend=True,
            title={
                'text': 'Service Profiles by Cluster',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1a237e'}
            },
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(x=0.02, y=0.98)
        )
        
        return fig
    
    def create_cluster_comparison_chart(self):
        """
        Create bar chart comparing clusters on key metrics
        """
        cluster_analysis = self.analyze_cluster_characteristics()
        
        cluster_ids = list(cluster_analysis.keys())
        satisfaction_rates = [cluster_analysis[cid]['satisfaction_rate'] for cid in cluster_ids]
        cluster_sizes = [cluster_analysis[cid]['size'] for cid in cluster_ids]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Satisfaction rate bars
        fig.add_trace(
            go.Bar(
                x=[f'Cluster {cid}' for cid in cluster_ids],
                y=satisfaction_rates,
                name='Satisfaction Rate (%)',
                marker_color='#4CAF50',
                yaxis='y',
                opacity=0.8
            ),
            secondary_y=False,
        )
        
        # Cluster size line
        fig.add_trace(
            go.Scatter(
                x=[f'Cluster {cid}' for cid in cluster_ids],
                y=cluster_sizes,
                mode='lines+markers',
                name='Cluster Size',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ),
            secondary_y=True,
        )
        
        # Update axes
        fig.update_xaxes(title_text="Customer Clusters")
        fig.update_yaxes(title_text="Satisfaction Rate (%)", secondary_y=False)
        fig.update_yaxes(title_text="Number of Customers", secondary_y=True)
        
        fig.update_layout(
            title={
                'text': 'Cluster Comparison: Satisfaction vs Size',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1a237e'}
            },
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(x=0.02, y=0.98)
        )
        
        return fig
    
    def generate_cluster_insights(self):
        """
        Generate actionable insights from cluster analysis
        """
        if 'Cluster' not in self.df.columns:
            self.perform_kmeans_clustering()
        
        cluster_analysis = self.analyze_cluster_characteristics()
        # n_clusters = len(cluster_analysis)  # 不再需要
        
        insights = []
        
        # Overall clustering quality
        silhouette = self.cluster_results['kmeans']['silhouette_score']
        if silhouette >= 0.5:
            quality = "Excellent"
            quality_color = "#4caf50"
        elif silhouette >= 0.3:
            quality = "Good"
            quality_color = "#ff9800"
        else:
            quality = "Fair"
            quality_color = "#f44336"
        
        insights.append(html.P([
            html.Span("🎯 Clustering Quality: ", style={'fontWeight': 'bold'}),
            html.Span(f"{quality} (Silhouette: {silhouette:.3f})", 
                     style={'color': quality_color, 'fontWeight': 'bold'})
        ], style={'margin': '5px 0', 'fontSize': '12px'}))
        
        return html.Div(insights)

def create_clustering_dashboard_component(df, service_attributes):
    """
    Create the complete clustering dashboard component for predictive analysis
    """
    # Initialize clustering analyzer
    analyzer = PassengerSegmentationAnalyzer(df, service_attributes)
    
    # Perform clustering analysis
    analyzer.perform_kmeans_clustering()
    analyzer.perform_pca_analysis()
    
    # Create visualizations
    pca_chart = analyzer.create_cluster_visualization('pca_scatter')
    comparison_chart = analyzer.create_cluster_visualization('cluster_comparison')
    
    # Generate insights
    insights = analyzer.generate_cluster_insights()
    
    # Create the dashboard component
    dashboard_component = html.Div([
        # Chart selection dropdown
        html.Div([
            html.Label("Clustering View:", style={'fontWeight': 'bold', 'fontSize': '12px'}),
            dcc.Dropdown(
                id='clustering-chart-selector',
                options=[
                    {'label': 'PCA Scatter Plot', 'value': 'pca_scatter'},
                    {'label': 'Cluster Comparison', 'value': 'cluster_comparison'},
                    {'label': 'Service Profiles', 'value': 'cluster_profiles'},
                ],
                value='pca_scatter',
                clearable=False,
                style={'fontSize': '12px', 'marginBottom': '10px'}
            )
        ], style={'marginBottom': '15px'}),
        
        # Chart area
        dcc.Graph(
            id='clustering-chart',
            figure=pca_chart,
            style={'height': '300px', 'marginBottom': '15px'},
            config={'displayModeBar': False}
        ),
        
        # Insights section
        html.Div([
            html.H6("🔍 Clustering Insights", 
                   style={'color': '#1a237e', 'fontSize': '14px', 'marginBottom': '10px'}),
            insights
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '10px',
            'borderRadius': '5px',
            'border': '1px solid #e0e0e0'
        })
    ])
    
    return dashboard_component, analyzer