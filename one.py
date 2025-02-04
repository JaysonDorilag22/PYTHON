from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
from pprint import pprint

# MongoDB configuration
mongo_url = "mongodb+srv://jaysondorilag1:se9fDvynepjCbW34@agapayalert-database.18wrk.mongodb.net/?retryWrites=true&w=majority&appName=AgapayAlert-Database"
DB_NAME = "test"
COLLECTION_NAME = "reports"

def connect_to_mongodb():
    try:
        client = MongoClient(mongo_url)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return client, collection
    except Exception as e:
        print(f"Connection error: {e}")
        return None, None

def prepare_data_for_analysis(collection):
    reports = list(collection.find())
    data = []
    for report in reports:
        try:
            record = {
                'type': report['type'],
                'barangay': report['location']['address']['barangay'],
                'city': report['location']['address']['city'],
                'age': report['personInvolved']['age'],
                'created_month': report['createdAt'].month,
                'created_day': report['createdAt'].weekday(),
                'created_hour': report['createdAt'].hour,
                'status': report['status'],
                'relationship': report['personInvolved']['relationship'],
                'lat': report['location']['coordinates'][1],  # Add coordinates
                'lon': report['location']['coordinates'][0]
            }
            data.append(record)
        except KeyError as e:
            print(f"Skipping record due to missing field: {e}")
    
    return pd.DataFrame(data)

def analyze_patterns(df):
    analysis = {
        'total_cases': len(df),
        'cases_by_type': df['type'].value_counts().to_dict(),
        'cases_by_barangay': df['barangay'].value_counts().to_dict(),
        'cases_by_status': df['status'].value_counts().to_dict(),
        'age_statistics': {
            'mean_age': df['age'].mean(),
            'median_age': df['age'].median(),
            'age_range': f"{df['age'].min()} - {df['age'].max()}"
        },
        'temporal_patterns': {
            'monthly_distribution': df['created_month'].value_counts().to_dict(),
            'day_distribution': df['created_day'].value_counts().to_dict(),
            'hour_distribution': df['created_hour'].value_counts().to_dict()
        }
    }
    return analysis

def train_prediction_model(df):
    # Prepare features
    X = pd.get_dummies(df.drop(['status'], axis=1))
    y = df['status']
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    accuracy = model.score(X_test, y_test)
    
    return model, accuracy, X.columns

def visualize_patterns(df):
    # Set style
    plt.style.use('seaborn')
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Case types
    sns.countplot(data=df, y='type', ax=ax1)
    ax1.set_title('Distribution of Case Types')
    
    # Age distribution
    sns.histplot(data=df, x='age', bins=20, ax=ax2)
    ax2.set_title('Age Distribution')
    
    # Monthly distribution
    sns.countplot(data=df, x='created_month', ax=ax3)
    ax3.set_title('Monthly Distribution')
    
    # Status distribution
    sns.countplot(data=df, y='status', ax=ax4)
    ax4.set_title('Case Status Distribution')
    
    plt.tight_layout()
    plt.savefig('analysis_results.png')
    plt.close()

def main():
    # Connect to MongoDB
    client, collection = connect_to_mongodb()
    if not client:
        return

    try:
        # Prepare data
        print("Preparing data...")
        df = prepare_data_for_analysis(collection)
        
        # Analyze patterns
        print("\nAnalyzing patterns...")
        patterns = analyze_patterns(df)
        print("\nPattern Analysis Results:")
        pprint(patterns)
        
        # Train predictive model
        print("\nTraining predictive model...")
        model, accuracy, feature_names = train_prediction_model(df)
        print(f"Model Accuracy: {accuracy:.2f}")
        
        # Visualize results
        print("\nGenerating visualizations...")
        visualize_patterns(df)
        print("Visualizations saved as 'analysis_results.png'")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    
    finally:
        client.close()
        print("\nMongoDB connection closed")

if __name__ == "__main__":
    main()