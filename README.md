# Airline Passenger Satisfaction Dashboard

A comprehensive visual analytics dashboard for analyzing airline passenger satisfaction data using machine learning and interactive visualizations.

## 📋 Overview

This dashboard provides airline decision-makers with powerful tools to understand customer satisfaction patterns, identify key service factors, and make data-driven improvements to enhance passenger experience.

### Key Features

- **Interactive Data Exploration**: Multiple visualization types including radar charts, parallel categories, and distribution plots
- **Machine Learning Insights**: Random Forest analysis for feature importance and satisfaction prediction
- **Customer Segmentation**: K-means clustering with PCA visualization for passenger grouping
- **Multi-dimensional Analysis**: Explore satisfaction patterns across different passenger demographics and travel characteristics
- **Real-time Filtering**: Dynamic sampling and subgroup analysis capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Required packages listed in `requirements.txt`

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd airline-satisfaction-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data**
   - Place your airline satisfaction dataset as `dataset/data2.csv`
   - Ensure the dataset follows the expected format (see Data Format section)

4. **Run the dashboard**
   ```bash
   python project.py
   ```

5. **Access the dashboard**
   - Open your browser and navigate to: `http://127.0.0.1:8050/`

## 📊 Dashboard Components

### 1. Dataset Overview
- **Summary Statistics**: Total passengers, satisfaction rate, average service score
- **Distribution Analysis**: Pie chart showing passenger distribution by selected demographics
- **Sample Size Control**: Adjustable sampling (1K, 5K, or All data)

### 2. Service Quality Radar
- **Multi-group Comparison**: Radar chart comparing service ratings across passenger subgroups
- **14 Service Factors**: Comprehensive analysis of all service touchpoints
- **Dynamic Grouping**: Switch between different demographic groupings

### 3. Service Factor Rankings
- **Random Forest Importance**: Machine learning-driven factor importance analysis
- **Subgroup-specific Insights**: Detailed analysis for each passenger segment
- **Model Accuracy**: Performance metrics for prediction reliability

### 4. Parallel Categories Flow
- **Customer Journey Visualization**: Flow analysis across multiple categorical dimensions
- **Customizable Dimensions**: Select up to 6 categories for flow analysis
- **Pattern Recognition**: Identify common passenger journey patterns

### 5. Passenger Segmentation
- **PCA Scatter Plot**: 2D visualization of passenger clusters
- **Segment Comparison**: Performance metrics across different clusters
- **Service Profiles**: Radar chart showing cluster-specific service preferences

## 📁 Project Structure

```
airline-satisfaction-dashboard/
├── project.py                 # Main application entry point
├── layout.py                  # Dashboard layout definition
├── preprocess.py             # Data preprocessing utilities
├── requirements.txt          # Python dependencies
├── utils.py                  # Utility functions and mappings
├── dataset/
│   └── data2.csv            # Airline satisfaction dataset
├── modules/
│   ├── Distribution.py      # Distribution chart components
│   ├── ParallelCategories.py # Parallel categories visualization
│   ├── RaderChart.py        # Radar chart implementation
│   ├── ServiceFactor.py     # Service factor analysis
│   ├── clustering.py        # Customer segmentation analysis
│   └── mlPredictor.py       # Machine learning prediction
└── README.md                # This file
```

## 📈 Data Format

Your dataset should include the following columns:

### Required Columns
- `satisfaction`: Customer satisfaction level ('satisfied' or 'neutral or dissatisfied')
- `Gender`: Passenger gender
- `Customer Type`: 'Loyal Customer' or 'Disloyal Customer'
- `Age`: Passenger age
- `Type of Travel`: 'Business travel' or 'Personal Travel'
- `Class`: Travel class ('Business', 'Eco', 'Eco Plus')
- `Flight Distance`: Distance in miles

### Service Rating Columns (0-5 scale)
- `Inflight wifi service`
- `Departure/Arrival time convenient`
- `Ease of Online booking`
- `Gate location`
- `Food and drink`
- `Online boarding`
- `Seat comfort`
- `Inflight entertainment`
- `On-board service`
- `Leg room service`
- `Baggage handling`
- `Checkin service`
- `Inflight service`
- `Cleanliness`

### Optional Columns
- `Departure Delay in Minutes`
- `Arrival Delay in Minutes`

## 🔧 Configuration

### Sampling Options
- **1K**: Quick analysis with 1,000 records
- **5K**: Balanced analysis with 5,000 records (default)
- **All**: Full dataset analysis (may be slower for large datasets)

### Customization
- Modify `utils.py` to adjust display names and value mappings
- Update `preprocess.py` to change age groupings or delay categories
- Adjust chart colors and styling in individual module files

## 🤖 Machine Learning Features

### Random Forest Analysis
- **Feature Importance**: Identifies which service factors most impact satisfaction
- **Subgroup Analysis**: Separate models for different passenger segments
- **Prediction Accuracy**: Model performance metrics displayed

### Customer Segmentation
- **K-means Clustering**: Automatic passenger grouping based on service preferences
- **PCA Visualization**: 2D representation of high-dimensional passenger data
- **Silhouette Scoring**: Clustering quality assessment

## 📋 Usage Examples

### Analyzing Business vs Economy Passengers
1. Set "Group by" to "Travel Class" in Dataset Overview
2. Select "Business" or "Eco" in Service Factor Rankings
3. Compare radar chart patterns between classes
4. Examine parallel categories flow for journey differences

### Identifying Key Service Improvements
1. Use Random Forest importance in Service Factor Rankings
2. Focus on high-importance, low-rating factors
3. Cross-reference with passenger segmentation insights
4. Prioritize improvements based on segment size and satisfaction impact

## 🛠️ Technical Dependencies

- **dash**: Web application framework
- **plotly**: Interactive visualization library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning algorithms
- **xgboost**: Gradient boosting framework
- **dash-bootstrap-components**: Bootstrap components for Dash

## 🔍 Troubleshooting

### Common Issues

1. **"No data available" errors**
   - Ensure `dataset/data2.csv` exists and has correct column names
   - Check that satisfaction column contains expected values

2. **Slow performance**
   - Reduce sample size to 1K or 5K
   - Check dataset size and consider data reduction

3. **Missing visualizations**
   - Verify all required packages are installed
   - Check browser console for JavaScript errors

4. **Random Forest errors**
   - Ensure sufficient data in each subgroup (minimum 30 samples)
   - Check that subgroups have both satisfied and dissatisfied customers

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Future Enhancements

- [ ] Real-time data integration
- [ ] Advanced SHAP (SHapley Additive exPlanations) analysis
- [ ] Export functionality for reports and insights
- [ ] Additional clustering algorithms (DBSCAN, Hierarchical)
- [ ] Time-series analysis for satisfaction trends
- [ ] Comparative analysis across multiple airlines

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Refer to the documentation in individual module files

---

**Built with ❤️ for data-driven airline service improvement**
