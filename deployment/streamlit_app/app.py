import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json

# Set page config
st.set_page_config(
    page_title="Conflict Early Warning System",
    page_icon="⚠️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px;
    }
    .warning-card {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 10px 0;
        border-radius: 5px;
    }
    .critical-card {
        background: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🌍 Conflict Early Warning System</h1>
    <p>Real-time monitoring and prediction of conflict risks using AI and social media analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/peace-dove.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Go to",
        ["Dashboard", "Real-time Analysis", "Historical Reports", "API Documentation", "About"]
    )
    
    st.divider()
    
    st.title("Settings")
    selected_regions = st.multiselect(
        "Select Regions",
        ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Meru", "Kakamega"],
        default=["Nairobi", "Mombasa", "Kisumu"]
    )
    
    date_range = st.date_input(
        "Select Date Range",
        [datetime.now() - timedelta(days=30), datetime.now()]
    )
    
    update_frequency = st.select_slider(
        "Update Frequency",
        options=["Realtime", "15min", "30min", "1hr", "6hr", "Daily"],
        value="30min"
    )

if page == "Dashboard":
    # Dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Total Analysis</h3>
            <h2>15,432</h2>
            <p>Social media posts analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ High Risk</h3>
            <h2>1,287</h2>
            <p>8.3% of total posts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Accuracy</h3>
            <h2>88%</h2>
            <p>Prediction accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⏱️ Processing</h3>
            <h2>50% faster</h2>
            <p>Than manual methods</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Map visualization
    st.subheader("🌍 Geographical Risk Map")
    
    # Sample map data
    map_data = pd.DataFrame({
        'lat': [-1.286389, -4.0435, -0.1022, -0.3031, 0.5143],
        'lon': [36.817223, 39.6682, 34.7617, 36.0800, 35.2698],
        'region': ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret'],
        'risk': [0.8, 0.6, 0.4, 0.7, 0.5],
        'size': [40, 30, 20, 35, 25]
    })
    
    fig = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lon",
        size="size",
        color="risk",
        hover_name="region",
        hover_data={"risk": ":.2f", "lat": False, "lon": False, "size": False},
        color_continuous_scale="RdYlGn_r",
        zoom=5.5,
        height=400
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap and timeline
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Risk Heatmap")
        
        # Sample heatmap data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        regions = selected_regions
        
        heatmap_data = pd.DataFrame({
            'date': np.repeat(dates, len(regions)),
            'region': np.tile(regions, len(dates)),
            'risk': np.random.uniform(0, 1, len(dates) * len(regions))
        })
        
        heatmap_pivot = heatmap_data.pivot(index='date', columns='region', values='risk')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values.T,
            x=heatmap_pivot.index,
            y=heatmap_pivot.columns,
            colorscale='RdYlGn_r',
            hoverongaps=False
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sentiment Timeline")
        
        # Sample timeline data
        timeline_data = pd.DataFrame({
            'date': dates,
            'sentiment': np.random.uniform(-1, 1, len(dates)),
            'intensity': np.random.uniform(0, 1, len(dates))
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_data['date'],
            y=timeline_data['sentiment'],
            mode='lines+markers',
            name='Sentiment',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Bar(
            x=timeline_data['date'],
            y=timeline_data['intensity'],
            name='Conflict Intensity',
            marker_color='red',
            opacity=0.6
        ))
        
        fig.update_layout(height=300, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    
    # Early warnings
    st.subheader("🚨 Early Warning Alerts")
    
    warnings_data = [
        {"type": "Sentiment Drop", "region": "Nairobi", "severity": "High", 
         "message": "Significant negative sentiment detected in last 24 hours"},
        {"type": "Conflict Cluster", "region": "Nakuru", "severity": "Critical",
         "message": "Multiple high-intensity conflict mentions"},
        {"type": "Protest Alert", "region": "Mombasa", "severity": "Medium",
         "message": "Protest-related keywords increasing"}
    ]
    
    for warning in warnings_data:
        card_class = "critical-card" if warning["severity"] == "Critical" else "warning-card"
        st.markdown(f"""
        <div class="{card_class}">
            <h4>⚠️ {warning['type']} - {warning['region']}</h4>
            <p><strong>Severity:</strong> {warning['severity']}</p>
            <p>{warning['message']}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Real-time Analysis":
    st.title("🔍 Real-time Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Live Twitter Feed Analysis")
        
        # Sample live data
        sample_tweets = [
            {"text": "Protest planned in Nairobi tomorrow #NairobiProtest", "risk": "High", "sentiment": -0.8},
            {"text": "Peaceful community meeting in Kisumu today", "risk": "Low", "sentiment": 0.7},
            {"text": "Clashes reported in Mombasa port area", "risk": "Critical", "sentiment": -0.9},
            {"text": "Government announces new peace initiative", "risk": "Low", "sentiment": 0.6},
            {"text": "Student demonstrations in Nakuru university", "risk": "Medium", "sentiment": -0.5}
        ]
        
        for tweet in sample_tweets:
            risk_color = {
                "Low": "green",
                "Medium": "orange",
                "High": "red",
                "Critical": "darkred"
            }.get(tweet["risk"], "gray")
            
            st.markdown(f"""
            <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; 
                        border-left: 5px solid {risk_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.1)">
                <p style="margin: 0;"><strong>{tweet['text']}</strong></p>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <span style="background: {risk_color}; color: white; padding: 3px 10px; border-radius: 15px;">
                        {tweet['risk']} Risk
                    </span>
                    <span>Sentiment: {tweet['sentiment']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Analysis Tools")
        
        # Manual text analysis
        st.text_area("Analyze Custom Text", 
                    "Enter text to analyze for conflict risk...",
                    height=150)
        
        if st.button("Analyze Text", type="primary"):
            st.success("Analysis complete!")
            st.metric("Risk Level", "Medium")
            st.metric("Sentiment Score", "-0.45")
            st.metric("Conflict Intensity", "0.62")
        
        st.divider()
        
        # Region selector
        selected_region = st.selectbox(
            "Focus Region",
            ["All Regions", "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"]
        )
        
        # Generate report
        if st.button("Generate Instant Report", type="secondary"):
            with st.spinner("Generating report..."):
                # Simulate API call
                import time
                time.sleep(2)
                
                st.success("Report generated!")
                st.download_button(
                    label="Download PDF Report",
                    data="Sample report content",
                    file_name="conflict_report.pdf",
                    mime="application/pdf"
                )

elif page == "Historical Reports":
    st.title("📁 Historical Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        month = st.selectbox("Select Month", 
                           ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"])
    
    with col2:
        year = st.selectbox("Select Year", [2024, 2023, 2022])
    
    if st.button("Generate Report", type="primary"):
        with st.spinner(f"Generating {month} {year} report..."):
            # Simulate report generation
            import time
            time.sleep(3)
            
            st.success("Report generated successfully!")
            
            # Display sample report
            st.subheader(f"{month} {year} Conflict Analysis Report")
            
            # Sample metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Posts Analyzed", "12,543", "15% increase")
            with col2:
                st.metric("High Risk Posts", "1,045", "8.3% of total")
            with col3:
                st.metric("Prediction Accuracy", "87.5%", "1.2% improvement")
            
            # Key findings
            st.subheader("Key Findings")
            findings = [
                "Nairobi showed highest conflict risk (72%)",
                "Mombasa had significant sentiment drop in week 3",
                "Overall risk decreased by 15% compared to previous month",
                "Peace initiatives showed positive impact in Kisumu"
            ]
            
            for finding in findings:
              st.markdown(f"✅ {finding}")
              
             # Regional analysis table
            st.subheader("Regional Risk Analysis")
            regional_data = pd.DataFrame({
                'Region': ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret'],
                'Risk Level': ['High', 'Medium', 'Low', 'High', 'Medium'],
                'Risk %': [72, 45, 28, 68, 42],
                'Sentiment': [-0.65, -0.32, 0.15, -0.58, -0.25],
                'Intensity': [0.82, 0.45, 0.28, 0.75, 0.38]
            })
            st.dataframe(regional_data.style.highlight_max(axis=0, subset=['Risk %', 'Intensity'], color='#ffcccc')
                                    .highlight_min(axis=0, subset=['Sentiment'], color='#ccffcc'),
                         use_container_width=True)
            
            # Recommendations
            st.subheader("Actionable Recommendations")
            recommendations = [
                "Increase peacekeeping patrols in Nairobi Central District",
                "Deploy conflict mediators to Nakuru County",
                "Launch community dialogue programs in Mombasa",
                "Monitor social media for protest organization in Eldoret"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. **{rec}**")
            
            # Download buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="📄 Download PDF Report",
                    data="Sample PDF content",
                    file_name=f"conflict_report_{month}_{year}.pdf",
                    mime="application/pdf"
                )
            with col2:
                st.download_button(
                    label="📊 Download Excel Data",
                    data="Sample Excel data",
                    file_name=f"conflict_data_{month}_{year}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            with col3:
                st.download_button(
                    label="📈 Download Visualizations",
                    data="Sample visualization files",
                    file_name=f"visualizations_{month}_{year}.zip",
                    mime="application/zip"
                )

elif page == "API Documentation":
    st.title("📚 API Documentation")
    
    st.markdown("""
    ## REST API Endpoints
    
    Our Conflict Early Warning System provides a RESTful API for programmatic access.
    
    ### Base URL
    ```
    https://api.conflict-early-warning.com/v1
    ```
    
    ### Authentication
    ```python
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    ```
    
    ### Available Endpoints
    """)
    
    # API endpoints table
    endpoints = [
        {
            "Method": "GET",
            "Endpoint": "/health",
            "Description": "Check API health status",
            "Example": "curl -X GET https://api.conflict-early-warning.com/v1/health"
        },
        {
            "Method": "POST",
            "Endpoint": "/predict",
            "Description": "Predict conflict risk from text",
            "Example": """curl -X POST https://api.conflict-early-warning.com/v1/predict \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"texts": ["Protest happening tomorrow"], "region": "Nairobi"}'
            """
        },
        {
            "Method": "GET",
            "Endpoint": "/reports/{month}/{year}",
            "Description": "Generate monthly report",
            "Example": "curl -X GET https://api.conflict-early-warning.com/v1/reports/january/2024"
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard",
            "Description": "Get dashboard data",
            "Example": "curl -X GET https://api.conflict-early-warning.com/v1/dashboard?region=Nairobi"
        }
    ]
    
    st.table(endpoints)
    
    st.markdown("""
    ### Python SDK Example
    ```python
    import conflict_early_warning as cew
    
    # Initialize client
    client = cew.Client(api_key="YOUR_API_KEY")
    
    # Make prediction
    result = client.predict(
        texts=["Violence reported in Nairobi"],
        region="Nairobi"
    )
    
    print(f"Risk Level: {result.risk_level}")
    print(f"Confidence: {result.confidence}")
    ```
    
    ### Rate Limits
    - Free tier: 100 requests/day
    - Pro tier: 10,000 requests/day
    - Enterprise: Unlimited
    """)
    
    # API testing interface
    st.subheader("🔧 API Testing Interface")
    
    endpoint = st.selectbox("Select Endpoint", ["/predict", "/health", "/dashboard"])
    method = st.selectbox("HTTP Method", ["GET", "POST"])
    
    if endpoint == "/predict":
        text_input = st.text_area("Text to Analyze", "Enter text here...")
        region = st.text_input("Region", "Nairobi")
        
        if st.button("Test Endpoint"):
            with st.spinner("Calling API..."):
                time.sleep(1)
                st.success("API call successful!")
                st.json({
                    "risk_level": "Medium",
                    "confidence": 0.87,
                    "sentiment": -0.45,
                    "recommendations": ["Monitor social media", "Increase patrols"]
                })

else:  # About page
    st.title("ℹ️ About This Project")
    
    st.markdown("""
    ## Conflict Early Warning System
    
    An AI-powered system for predicting and monitoring conflict risks using social media analysis,
    machine learning, and real-time data processing.
    
    ### 🎯 Mission
    To provide early warnings of potential conflicts through data-driven insights, 
    enabling proactive peacekeeping and conflict prevention.
    
    ### 🔬 Technology Stack
    - **Backend**: Python, FastAPI, PostgreSQL
    - **Machine Learning**: Scikit-learn, TensorFlow, NLP libraries
    - **Data Processing**: Apache Spark, Pandas, NumPy
    - **Visualization**: Tableau, Plotly, Streamlit
    - **Deployment**: Docker, AWS, GitHub Actions
    
    ### 📊 Key Features
    1. **Real-time Monitoring**: Continuous analysis of social media streams
    2. **Predictive Analytics**: 88% accurate conflict prediction
    3. **Geospatial Intelligence**: Location-based risk mapping
    4. **Automated Reporting**: Monthly actionable insights
    5. **Early Warning Alerts**: Proactive risk notifications
    
    ### 👨‍💻 Author
    **Kiprop Gibson Ngetich**
    - Data Scientist | AI & Machine Learning Specialist
    - Email: kipropgibson13@gmail.com
    - LinkedIn: [linkedin.com/in/ngetichgibson](https://linkedin.com/in/ngetichgibson)
    - Portfolio: [gbgibson7.github.io](https://gbgibson7.github.io)
    - GitHub: [github.com/GbGibson7](https://github.com/GbGibson7)
    
    ### 📄 License
    MIT License - See LICENSE file for details
    
    ### 🤝 Contributing
    Contributions are welcome! Please read our contributing guidelines.
    """)
    
    # Contact form
    st.subheader("📬 Contact Us")
    
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message", height=150)
        
        submitted = st.form_submit_button("Send Message")
        if submitted:
            st.success("Thank you for your message! We'll get back to you soon.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; padding: 20px;">
    <p>Conflict Early Warning System v1.0.0 | © 2024 Kiprop Gibson Ngetich</p>
    <p>Built with ❤️ for peace and security</p>
    <p>
        <a href="https://github.com/GbGibson7/conflict-early-warning" target="_blank">GitHub</a> | 
        <a href="https://linkedin.com/in/ngetichgibson" target="_blank">LinkedIn</a> | 
        <a href="mailto:kipropgibson13@gmail.com">Email</a>
    </p>
</div>
""", unsafe_allow_html=True)           