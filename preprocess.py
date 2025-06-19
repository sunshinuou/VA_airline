import pandas as pd

def preprocess_airline_data(df):
    """
    Robust data preprocessing with error handling
    """
    if df is None:
        return None, None
    
    df_processed = df.copy()
    
    print("=== DATA PREPROCESSING ===")
    print(f"Original shape: {df_processed.shape}")
    
    # 1. Handle missing values
    missing_summary = df_processed.isnull().sum()
    
    
    # Handle arrival delay missing values
    if 'Arrival Delay in Minutes' in df_processed.columns:
        before_fill = df_processed['Arrival Delay in Minutes'].isnull().sum()
        df_processed['Arrival Delay in Minutes'] = df_processed['Arrival Delay in Minutes'].fillna(0)
        
    # Remove rows with missing satisfaction data (critical for analysis)
    if 'satisfaction' in df_processed.columns:
        before_drop = len(df_processed)
        df_processed = df_processed.dropna(subset=['satisfaction'])
        after_drop = len(df_processed)
        if before_drop != after_drop:
            print(f"Dropped {before_drop - after_drop} rows with missing satisfaction data")
    
    # 2. Data type conversions and cleaning
    print(f"\nProcessed shape: {df_processed.shape}")
    
    # Ensure satisfaction is properly encoded
    if 'satisfaction' in df_processed.columns:
        df_processed['satisfaction_binary'] = (df_processed['satisfaction'] == 'satisfied').astype(int)
        satisfaction_counts = df_processed['satisfaction'].value_counts()
        
    # Create age groups for better analysis
    if 'Age' in df_processed.columns:
        age_labels = ['Young (≤25)', 'Adult (26-40)', 'Middle-aged (41-60)', 'Senior (>60)']
        df_processed['Age_Group'] = pd.cut(df_processed['Age'], 
                                         bins=[0, 25, 40, 60, 100], 
                                         labels=age_labels)
        df_processed['Age_Group'] = pd.Categorical(df_processed['Age_Group'], categories=age_labels, ordered=True)
    
    # Create delay categories
    if 'Departure Delay in Minutes' in df_processed.columns:
        df_processed['Departure_Delay_Category'] = pd.cut(df_processed['Departure Delay in Minutes'],
                                                         bins=[-1, 0, 15, 60, float('inf')],
                                                         labels=['No Delay', 'Short (1-15min)', 'Medium (16-60min)', 'Long (>60min)'])
    
    # Create arrival delay categories
    if 'Arrival Delay in Minutes' in df_processed.columns:
        df_processed['Arrival_Delay_Category'] = pd.cut(df_processed['Arrival Delay in Minutes'],
                                                       bins=[-1, 0, 15, 60, float('inf')],
                                                       labels=['No Delay', 'Short (1-15min)', 'Medium (16-60min)', 'Long (>60min)'])
    
    # 3. Define service attributes for analysis
    potential_service_attributes = [
        'Inflight wifi service', 'Departure/Arrival time convenient', 
        'Ease of Online booking', 'Gate location', 'Food and drink',
        'Online boarding', 'Seat comfort', 'Inflight entertainment',
        'On-board service', 'Leg room service', 'Baggage handling',
        'Checkin service', 'Inflight service', 'Cleanliness'
    ]
    
    # Only include attributes that exist in the dataset
    service_attributes = [attr for attr in potential_service_attributes if attr in df_processed.columns]
    #print(f"\nFound {len(service_attributes)} service attributes:")
    #for attr in service_attributes:
        #print(f"  - {attr}")
    
    # 4. Validate and clean service ratings
    for attr in service_attributes:
        # Check the range of values
        min_val = df_processed[attr].min()
        max_val = df_processed[attr].max()
        
        
        # Clip values to valid range if needed (assuming 1-5 or 0-5 scale)
        if min_val >= 0 and max_val <= 5:
            df_processed[attr] = df_processed[attr].clip(0, 5)
        elif min_val >= 1 and max_val <= 5:
            df_processed[attr] = df_processed[attr].clip(1, 5)
    
    # 5. Create composite scores
    if service_attributes:
        df_processed['Service_Quality_Score'] = df_processed[service_attributes].mean(axis=1)
        
    # 6. Feature engineering for subgroup analysis
    if 'Type of Travel' in df_processed.columns and 'Class' in df_processed.columns:
        df_processed['Travel_Experience'] = df_processed['Type of Travel'] + '_' + df_processed['Class']
    
    print("=== PREPROCESSING COMPLETE ===")
    return df_processed, service_attributes 