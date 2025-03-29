import dash
from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = 'Film Revenue Visualization'

# Load the dataset
df = pd.read_csv("data/combined.csv")

# Extract production countries from JSON
def extract_countries(countries_json):
    try:
        # Replace double quotes with single quotes if needed
        if isinstance(countries_json, str):
            countries_json = countries_json.replace('""', '"')
            # Parse the JSON
            countries_list = json.loads(countries_json)
            # Extract country names
            return [country['name'] for country in countries_list]
        return []
    except Exception as e:
        print(f"Error extracting countries: {e}")
        print(f"Problematic JSON: {countries_json}")
        return []

# Apply the function to extract production countries
df['production_countries_list'] = df['production_countries'].apply(extract_countries)

# Filter for films with revenue > 10 million
high_revenue_films = df[df['revenue'] > 10000000]

# Explode the DataFrame to have one row per country
df_exploded = high_revenue_films.explode('production_countries_list').rename(columns={'production_countries_list': 'country'})

# Remove rows with NaN countries
df_exploded = df_exploded[~df_exploded['country'].isna()]

# Count films by country
country_counts = df_exploded.groupby('country').size().reset_index(name='count')

# Sort by count in descending order and take top 15 countries (for better visibility)
top_countries = country_counts.sort_values('count', ascending=False).head(15)

# Create figure
fig = go.Figure()

# Define cube size and spacing
cube_size = 0.1
y_spacing = 1.5

# For each country, create a row of cubes
for i, (_, row) in enumerate(top_countries.iterrows()):
    country = row['country']
    count = row['count']
    
    # Create x and y coordinates for each cube
    y_pos = i * y_spacing
    
    for j in range(count):
        x_pos = j
        
        # Add a cube (square marker) for each film
        fig.add_trace(go.Scatter(
            x=[x_pos],
            y=[y_pos],
            mode='markers',
            marker=dict(
                symbol='square',
                size=cube_size * 50,  # Size in pixels
                color='#1f77b4',  # Blue color
                line=dict(width=1, color='rgba(0,0,0,0.5)')
            ),
            showlegend=False,
            hoverinfo='text',
            text=f"{country}: Film #{j+1}"
        ))

# Calculate y-positions for each country label
y_positions = [i * y_spacing for i in range(len(top_countries))]

# Update layout
fig.update_layout(
    title='Number of Films with Revenue > $10 Million by Country',
    xaxis=dict(
        title='Number of Films',
        showgrid=True,
        zeroline=False,
        range=[-1, max(top_countries['count']) + 1]
    ),
    yaxis=dict(
        tickvals=y_positions,  # Fixed: use calculated positions
        ticktext=top_countries['country'].tolist(),
        zeroline=False,
        showgrid=False
    ),
    height=800,
    margin=dict(l=150, r=20, t=50, b=50),
    plot_bgcolor='rgba(240,240,240,0.8)'
)

# Create the Dash layout
app.layout = html.Div([
    html.H1("Film Production by Country (Revenue > $10M)"),
    html.P("Horizontal histogram showing films as individual cubes, where each cube represents one film that generated more than $10 million"),
    dcc.Graph(figure=fig)
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
