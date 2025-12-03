import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class DashboardGenerator:
    def __init__(self):
        self.colors = {
            'critical': '#FF0000',
            'high': '#FF6B6B',
            'medium': '#FFD166',
            'low': '#06D6A0',
            'safe': '#118AB2'
        }
    
    def generate_conflict_heatmap(self, df: pd.DataFrame, date_column: str = 'date') -> go.Figure:
        """Generate conflict heatmap over time"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Aggregate by date and region
        heatmap_data = df.groupby([date_column, 'region'])['conflict_risk'].mean().unstack()
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.index,
            y=heatmap_data.columns,
            colorscale='RdYlGn_r',  # Red for high risk
            colorbar=dict(title='Risk Level'),
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Conflict Risk Heatmap Over Time',
            xaxis_title='Date',
            yaxis_title='Region',
            height=500
        )
        
        return fig
    
    def generate_sentiment_timeline(self, df: pd.DataFrame) -> go.Figure:
        """Generate sentiment timeline with risk alerts"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['created_at'])
        
        # Resample to daily
        daily_sentiment = df.resample('D', on='date').agg({
            'vader_compound': 'mean',
            'conflict_intensity': 'mean',
            'total_engagement': 'sum'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Sentiment Trend', 'Conflict Intensity'),
            vertical_spacing=0.15
        )
        
        # Sentiment line
        fig.add_trace(
            go.Scatter(
                x=daily_sentiment['date'],
                y=daily_sentiment['vader_compound'],
                mode='lines+markers',
                name='Sentiment',
                line=dict(color='blue', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 0, 255, 0.1)'
            ),
            row=1, col=1
        )
        
        # Conflict intensity bars
        fig.add_trace(
            go.Bar(
                x=daily_sentiment['date'],
                y=daily_sentiment['conflict_intensity'],
                name='Conflict Intensity',
                marker_color=daily_sentiment['conflict_intensity'].apply(
                    lambda x: self._get_color_from_intensity(x)
                )
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=True)
        fig.update_xaxes(title_text='Date', row=2, col=1)
        fig.update_yaxes(title_text='Sentiment Score', row=1, col=1)
        fig.update_yaxes(title_text='Conflict Intensity', row=2, col=1)
        
        return fig
    
    def _get_color_from_intensity(self, intensity: float) -> str:
        """Get color based on conflict intensity"""
        if intensity > 0.7:
            return self.colors['critical']
        elif intensity > 0.5:
            return self.colors['high']
        elif intensity > 0.3:
            return self.colors['medium']
        else:
            return self.colors['low']
    
    def generate_geographical_map(self, df: pd.DataFrame) -> go.Figure:
        """Generate geographical map with conflict markers"""
        # Sample data - you would use actual coordinates
        regions = {
            'Nairobi': {'lat': -1.286389, 'lon': 36.817223, 'risk': 0.8},
            'Mombasa': {'lat': -4.0435, 'lon': 39.6682, 'risk': 0.6},
            'Kisumu': {'lat': -0.1022, 'lon': 34.7617, 'risk': 0.4},
            'Nakuru': {'lat': -0.3031, 'lon': 36.0800, 'risk': 0.7},
            'Eldoret': {'lat': 0.5143, 'lon': 35.2698, 'risk': 0.5}
        }
        
        fig = go.Figure()
        
        for region, data in regions.items():
            fig.add_trace(go.Scattermapbox(
                lat=[data['lat']],
                lon=[data['lon']],
                mode='markers+text',
                marker=dict(
                    size=20 + data['risk'] * 30,
                    color=self._get_color_from_intensity(data['risk']),
                    opacity=0.8
                ),
                text=[region],
                textposition='top center',
                name=region,
                hovertext=f"Risk Level: {data['risk']:.1%}",
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title='Conflict Risk Map',
            mapbox=dict(
                style='carto-positron',
                zoom=5.5,
                center=dict(lat=-0.0236, lon=37.9062)  # Center of Kenya
            ),
            height=500,
            showlegend=True
        )
        
        return fig
    
    def generate_monthly_report(self, df: pd.DataFrame, month: str, year: int) -> dict:
        """Generate comprehensive monthly report"""
        report_data = {
            'month': month,
            'year': year,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {},
            'regional_analysis': {},
            'trends': {},
            'recommendations': []
        }
        
        # Overall statistics
        total_tweets = len(df)
        high_risk_tweets = len(df[df['risk_level'].isin(['High', 'Critical'])])
        
        report_data['summary'] = {
            'total_tweets_analyzed': total_tweets,
            'high_risk_tweets': high_risk_tweets,
            'high_risk_percentage': (high_risk_tweets / total_tweets * 100) if total_tweets > 0 else 0,
            'average_sentiment': df['vader_compound'].mean(),
            'average_conflict_intensity': df['conflict_intensity'].mean()
        }
        
        # Regional analysis
        regional_stats = df.groupby('region').agg({
            'vader_compound': 'mean',
            'conflict_intensity': 'mean',
            'risk_level': lambda x: (x.isin(['High', 'Critical']).sum() / len(x) * 100)
        }).round(2)
        
        report_data['regional_analysis'] = regional_stats.to_dict()
        
        # Key findings
        top_high_risk_regions = regional_stats.nlargest(3, 'risk_level').index.tolist()
        report_data['key_findings'] = {
            'top_high_risk_regions': top_high_risk_regions,
            'most_negative_sentiment_region': regional_stats['vader_compound'].idxmin(),
            'highest_conflict_intensity_region': regional_stats['conflict_intensity'].idxmax()
        }
        
        # Recommendations
        for region in top_high_risk_regions:
            report_data['recommendations'].append(
                f"Increase monitoring and peacekeeping presence in {region}"
            )
        
        # Add trend analysis
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['week'] = df['date'].dt.isocalendar().week
                            weekly_trends = df.groupby('week').agg({
                    'vader_compound': 'mean',
                    'conflict_intensity': 'mean',
                    'risk_level': lambda x: (x.isin(['High', 'Critical']).sum() / len(x) * 100)
                }).reset_index()
                
                report_data['trends'] = {
                    'weekly_sentiment_trend': weekly_trends['vader_compound'].tolist(),
                    'weekly_intensity_trend': weekly_trends['conflict_intensity'].tolist(),
                    'weekly_risk_trend': weekly_trends['risk_level'].tolist(),
                    'peak_risk_week': weekly_trends.loc[weekly_trends['risk_level'].idxmax(), 'week']
                }
        
        # Early warning alerts
        report_data['early_warnings'] = self._generate_early_warnings(df)
        
        return report_data
    
    def _generate_early_warnings(self, df: pd.DataFrame) -> list:
        """Generate early warning alerts based on data patterns"""
        warnings = []
        
        # Check for sudden sentiment drops
        if 'vader_compound' in df.columns and 'date' in df.columns:
            df_sorted = df.sort_values('date')
            recent_sentiment = df_sorted['vader_compound'].tail(7).mean()
            previous_sentiment = df_sorted['vader_compound'].tail(14).head(7).mean()
            
            if recent_sentiment < previous_sentiment - 0.3:  # Significant drop
                warnings.append({
                    'type': 'sentiment_drop',
                    'severity': 'high',
                    'message': f"Significant sentiment drop detected: {recent_sentiment:.2f} vs {previous_sentiment:.2f}",
                    'suggested_action': 'Monitor social media for potential unrest triggers'
                })
        
        # Check for increasing conflict intensity
        if 'conflict_intensity' in df.columns:
            high_intensity_count = len(df[df['conflict_intensity'] > 0.7])
            if high_intensity_count > 10:  # Threshold
                warnings.append({
                    'type': 'high_intensity_cluster',
                    'severity': 'critical',
                    'message': f"{high_intensity_count} high-intensity conflict mentions detected",
                    'suggested_action': 'Deploy rapid response teams to affected regions'
                })
        
        return warnings
    
    def generate_html_report(self, report_data: dict, output_path: str = None) -> str:
        """Generate HTML report from report data"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Conflict Early Warning Report - {report_data['month']} {report_data['year']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; border-radius: 10px; }}
                .section {{ background: white; padding: 25px; margin: 20px 0; border-radius: 10px; 
                          box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; 
                              text-align: center; margin: 10px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; 
                          margin: 10px 0; }}
                .critical {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
                .recommendation {{ background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; 
                                margin: 10px 0; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                              gap: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Conflict Early Warning System Report</h1>
                <h2>{report_data['month']} {report_data['year']}</h2>
                <p>Generated: {report_data['generated_date']}</p>
            </div>
            
            <div class="section">
                <h3>📊 Executive Summary</h3>
                <div class="metric-grid">
                    <div class="metric-card">
                        <h4>Total Tweets Analyzed</h4>
                        <h2>{report_data['summary']['total_tweets_analyzed']:,}</h2>
                    </div>
                    <div class="metric-card">
                        <h4>High Risk Tweets</h4>
                        <h2>{report_data['summary']['high_risk_tweets']:,}</h2>
                    </div>
                    <div class="metric-card">
                        <h4>High Risk Percentage</h4>
                        <h2>{report_data['summary']['high_risk_percentage']:.1f}%</h2>
                    </div>
                    <div class="metric-card">
                        <h4>Average Sentiment</h4>
                        <h2>{report_data['summary']['average_sentiment']:.3f}</h2>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3>⚠️ Early Warning Alerts</h3>
                {self._generate_warnings_html(report_data.get('early_warnings', []))}
            </div>
            
            <div class="section">
                <h3>📍 Regional Risk Analysis</h3>
                {self._generate_regional_table_html(report_data['regional_analysis'])}
            </div>
            
            <div class="section">
                <h3>🎯 Key Findings</h3>
                <ul>
                    <li><strong>Top High-Risk Regions:</strong> {', '.join(report_data['key_findings']['top_high_risk_regions'])}</li>
                    <li><strong>Most Negative Sentiment:</strong> {report_data['key_findings']['most_negative_sentiment_region']}</li>
                    <li><strong>Highest Conflict Intensity:</strong> {report_data['key_findings']['highest_conflict_intensity_region']}</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>📈 Actionable Recommendations</h3>
                {self._generate_recommendations_html(report_data['recommendations'])}
            </div>
        </body>
        </html>
        """
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            print(f"HTML report saved to {output_path}")
        
        return html_template
    
    def _generate_warnings_html(self, warnings: list) -> str:
        """Generate HTML for warnings section"""
        if not warnings:
            return '<p>✅ No critical warnings this period.</p>'
        
        html = ''
        for warning in warnings:
            severity_class = 'warning critical' if warning['severity'] == 'critical' else 'warning'
            html += f"""
            <div class="{severity_class}">
                <h4>🚨 {warning['type'].replace('_', ' ').title()}</h4>
                <p><strong>Message:</strong> {warning['message']}</p>
                <p><strong>Suggested Action:</strong> {warning['suggested_action']}</p>
            </div>
            """
        return html
    
    def _generate_regional_table_html(self, regional_data: dict) -> str:
        """Generate HTML table for regional analysis"""
        if not regional_data:
            return '<p>No regional data available.</p>'
        
        # Convert dict to DataFrame for easier manipulation
        df = pd.DataFrame(regional_data).T
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #667eea; color: white;">'
        html += '<th style="padding: 12px; text-align: left;">Region</th>'
        html += '<th style="padding: 12px; text-align: left;">Sentiment</th>'
        html += '<th style="padding: 12px; text-align: left;">Intensity</th>'
        html += '<th style="padding: 12px; text-align: left;">Risk %</th>'
        html += '</tr>'
        
        for idx, (region, data) in enumerate(df.iterrows()):
            bg_color = '#f2f2f2' if idx % 2 == 0 else 'white'
            risk_color = self._get_risk_color(data.get('risk_level', 0))
            
            html += f'<tr style="background: {bg_color};">'
            html += f'<td style="padding: 10px; border: 1px solid #ddd;">{region}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #ddd;">{data.get("vader_compound", 0):.3f}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #ddd;">{data.get("conflict_intensity", 0):.3f}</td>'
            html += f'<td style="padding: 10px; border: 1px solid #ddd; background: {risk_color};">{data.get("risk_level", 0):.1f}%</td>'
            html += '</tr>'
        
        html += '</table>'
        return html
    
    def _get_risk_color(self, risk_percentage: float) -> str:
        """Get color based on risk percentage"""
        if risk_percentage > 70:
            return '#FF0000'
        elif risk_percentage > 50:
            return '#FF6B6B'
        elif risk_percentage > 30:
            return '#FFD166'
        else:
            return '#06D6A0'
    
    def _generate_recommendations_html(self, recommendations: list) -> str:
        """Generate HTML for recommendations"""
        if not recommendations:
            return '<p>No specific recommendations for this period.</p>'
        
        html = ''
        for i, rec in enumerate(recommendations, 1):
            html += f"""
            <div class="recommendation">
                <h4>✅ Recommendation {i}</h4>
                <p>{rec}</p>
            </div>
            """
        return html
            