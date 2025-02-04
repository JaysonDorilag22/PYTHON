import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium import plugins
from streamlit_folium import folium_static
from one import connect_to_mongodb, prepare_data_for_analysis, train_prediction_model
import pandas as pd
from datetime import datetime, timedelta

def create_map(df):
    # Create base map centered on Taguig
    m = folium.Map(location=[14.5176, 121.0509], zoom_start=13)
    
    # Add heatmap layer
    heat_data = [[row['lat'], row['lon'], 1] for _, row in df.iterrows()]
    plugins.HeatMap(heat_data).add_to(m)
    
    # Add markers for incidents
    for _, row in df.iterrows():
        color = 'red' if row['status'] == 'Pending' else 'blue'
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=f"Type: {row['type']}<br>Status: {row['status']}<br>Age: {row['age']}",
            color=color,
            fill=True
        ).add_to(m)
    
    return m

def create_dashboard():
    st.title('AgapayAlert Analytics Dashboard')
    
    # Connect and get data
    client, collection = connect_to_mongodb()
    df = prepare_data_for_analysis(collection)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Statistics", "Predictive Map", "Risk Analysis"])
    
    with tab1:
        # Sidebar filters
        st.sidebar.header('Filters')
        selected_barangay = st.sidebar.multiselect(
            'Select Barangay',
            options=df['barangay'].unique(),
            default=df['barangay'].unique()
        )
        
        # Filter data
        filtered_df = df[df['barangay'].isin(selected_barangay)]
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cases", len(filtered_df))
        with col2:
            st.metric("Average Age", f"{filtered_df['age'].mean():.1f}")
        with col3:
            st.metric("Active Cases", len(filtered_df[filtered_df['status'] == 'Pending']))
        with col4:
            st.metric("Resolution Rate", 
                     f"{(1 - len(filtered_df[filtered_df['status'] == 'Pending'])/len(filtered_df)):.1%}")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Case Types Distribution
            fig_types = px.pie(filtered_df, names='type', title='Distribution of Case Types')
            st.plotly_chart(fig_types, use_container_width=True)
            
            # Age Distribution
            fig_age = px.histogram(filtered_df, x='age', title='Age Distribution', nbins=20)
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Status Distribution
            fig_status = px.bar(filtered_df['status'].value_counts(), title='Cases by Status')
            st.plotly_chart(fig_status, use_container_width=True)
            
            # Temporal Heat Map
            pivot_data = filtered_df.pivot_table(
                index='created_day',
                columns='created_hour',
                values='type',
                aggfunc='count'
            ).fillna(0)
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=pivot_data.values,
                x=pivot_data.columns,
                y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                colorscale='Viridis'
            ))
            fig_heatmap.update_layout(
                title='Cases by Day and Hour',
                xaxis_title='Hour of Day',
                yaxis_title='Day of Week'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab2:
        st.header("Geographical Analysis & Predictions")
        
        # Create and display map
        m = create_map(filtered_df)
        folium_static(m)
        
        # Predictive insights
        st.subheader("Predictive Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            # Train model and get predictions
            model, accuracy, _ = train_prediction_model(filtered_df)
            st.metric("Model Accuracy", f"{accuracy:.1%}")
            
            # High-risk areas
            risk_areas = filtered_df['barangay'].value_counts().head()
            st.write("High-Risk Areas:")
            st.bar_chart(risk_areas)
        
        with col2:
            # Time-based patterns
            st.write("Peak Incident Hours:")
            hourly_incidents = filtered_df['created_hour'].value_counts().sort_index()
            st.line_chart(hourly_incidents)
    
    with tab3:
        st.header("Risk Assessment Dashboard")
        
        # Risk metrics
        risk_score = len(filtered_df[filtered_df['status'] == 'Pending']) / len(filtered_df)
        st.metric("Overall Risk Score", f"{risk_score:.2%}")
        
        # Risk factors analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Factors")
            risk_factors = pd.DataFrame({
                'Factor': ['Time of Day', 'Location', 'Age Group', 'Case Type'],
                'Risk Level': ['High', 'Medium', 'Low', 'Medium']
            })
            st.table(risk_factors)
        
        with col2:
            st.subheader("Recommendations")
            st.write("1. Increase patrols during peak hours")
            st.write("2. Focus resources in high-risk areas")
            st.write("3. Implement preventive measures")
            st.write("4. Enhanced monitoring of pending cases")

if __name__ == '__main__':
    create_dashboard()