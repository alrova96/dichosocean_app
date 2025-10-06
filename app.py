"""
DICHOSOCEAN Intelligence Panel
===============================
A Streamlit-based data visualization and analysis platform for oceanographic data
collected by biogeochemical sensors deployed in the Antarctic DICHOSO project.

Author: Dr. Alejandro Román
Institution: ICMAN-CSIC
Date: 2024-2025

This application provides interactive visualizations and statistical analysis of
oceanographic variables including temperature, salinity, pH, chlorophyll-a, turbidity,
dissolved oxygen, pCO2, and total alkalinity collected from Deception Island, Antarctica.
"""

# =============================================================================
# IMPORTS
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
from datetime import datetime, timedelta
import random

# =============================================================================
# COLOR PALETTES
# =============================================================================
# UI colors for main interface elements
UI_COLORS = {
    'primary': '#022B3A',        # Dark blue for main elements
    'secondary': '#1F7A8C',      # Medium blue for secondary elements
    'light_blue': '#BFDBF7',     # Light blue for backgrounds
    'light_gray': '#E1E5F2',     # Light gray for sections
    'white': '#FFFFFF'           # White for text/backgrounds
}

# Chart colors - gradient from cool (blues) to warm (reds/oranges)
# Used for data visualizations to represent different variables or categories
CHART_COLORS = [
    '#001219',  # Dark blue (cold)
    '#005F73',  # Blue
    '#0A9396',  # Cyan
    '#94D2BD',  # Light cyan/green
    '#E9D8A6',  # Beige (neutral)
    '#EE9B00',  # Orange
    '#CA6702',  # Dark orange
    '#BB3E03',  # Red-orange
    '#AE2012',  # Red
    '#9B2226'   # Dark red (warm)
]

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
# Configure Streamlit page settings
st.set_page_config(
    page_title="DICHOSOCEAN Intelligence Panel",
    page_icon="🌊",
    layout="wide",                          # Use full width of browser
    initial_sidebar_state="expanded"        # Show sidebar by default
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================
# Apply custom CSS styles to enhance the appearance of the Streamlit app
st.markdown(f"""
<style>
    /* Main header styling with gradient background */
    .main-header {{
        background: linear-gradient(90deg, {UI_COLORS['primary']} 0%, {UI_COLORS['secondary']} 100%);
        padding: 2rem;
        border-radius: 10px;
        color: {UI_COLORS['white']};
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* Metric card styling for key statistics */
    .metric-card {{
        background: {UI_COLORS['light_blue']};
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid {UI_COLORS['secondary']};
        margin: 1rem 0;
    }}

    /* Section header styling */
    .section-header {{
        background: {UI_COLORS['light_gray']};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {UI_COLORS['primary']};
        margin: 1rem 0;
    }}

    /* Sidebar background color */
    [data-testid="stSidebar"] {{
        background-color: #001219;
    }}

    /* Sidebar text color - apply to all elements */
    [data-testid="stSidebar"] * {{
        color: #E9D8A6 !important;
    }}

    /* Sidebar input field text color */
    [data-testid="stSidebar"] input {{
        color: #001219 !important;
    }}

    /* Sidebar input wrapper text color */
    [data-testid="stSidebar"] [data-baseweb="input"] {{
        color: #001219 !important;
    }}

    /* Center-align sidebar headers */
    [data-testid="stSidebar"] h3 {{
        text-align: center !important;
    }}

    /* Center-align sidebar labels */
    [data-testid="stSidebar"] label {{
        text-align: center !important;
        justify-content: center !important;
    }}

    /* Center-align sidebar text inputs */
    [data-testid="stSidebar"] input[type="text"] {{
        text-align: center !important;
    }}

    /* Center-align sidebar input wrapper contents */
    [data-testid="stSidebar"] [data-baseweb="input"] input {{
        text-align: center !important;
    }}

    /* Navigation button base styling */
    .nav-button {{
        background-color: transparent;
        border: none;
        color: #E9D8A6;
        padding: 0.75rem 1rem;
        text-align: left;
        width: 100%;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.2s;
        font-size: 1rem;
        margin: 0.2rem 0;
    }}

    /* Navigation button hover effect */
    .nav-button:hover {{
        background-color: rgba(233, 216, 166, 0.1);
    }}

    /* Active navigation button styling */
    .nav-button-active {{
        background-color: rgba(233, 216, 166, 0.2);
        border-left: 3px solid #E9D8A6;
    }}

    /* Streamlit button styling */
    .stButton > button {{
        background-color: {UI_COLORS['secondary']};
        color: {UI_COLORS['white']};
        border: none;
        border-radius: 5px;
        transition: all 0.3s;
    }}

    /* Streamlit button hover effect */
    .stButton > button:hover {{
        background-color: {UI_COLORS['primary']};
        transform: translateY(-2px);
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

@st.cache_data
def load_data():
    """
    Load and preprocess oceanographic data from CSV file with outlier removal.

    This function:
    1. Reads the prepared CSV file containing oceanographic measurements
    2. Renames columns to standardized format for easier processing
    3. Converts datetime strings to datetime objects
    4. Removes outliers from specific variables using domain-specific thresholds

    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe with outliers removed
    """
    # Read the prepared CSV file
    df = pd.read_csv('data/dichosocean_prepared.csv')

    # Rename columns to match the app's expected format
    # This standardizes column names for easier reference throughout the code
    df = df.rename(columns={
        'DateTime (UTC+00:00)': 'datetime',
        'Temperature (ºC)': 'temperature',
        'Pressure (dbar)': 'pressure',
        'Chlorophyll (ug/L)': 'chlorophyll_a',
        'Turbidity (NTU)': 'turbidity',
        'Salinity (PSU)': 'salinity',
        'pH': 'ph',
        'OD umolKg-1': 'dissolved_oxygen',
        'pCO2': 'pco2',
        'TA (ueq/kg)': 'ta'
    })

    # Convert datetime column to datetime type for proper time series handling
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Remove outliers using domain-specific thresholds
    # Chlorophyll-a: Remove values above 200 μg/L (unrealistically high for this region)
    df.loc[df['chlorophyll_a'] > 200, 'chlorophyll_a'] = np.nan

    # Turbidity: Remove exceptionally high values using 99th percentile as threshold
    # This is a statistical approach to remove extreme outliers while preserving variability
    turbidity_threshold = df['turbidity'].quantile(0.99)
    df.loc[df['turbidity'] > turbidity_threshold, 'turbidity'] = np.nan

    # Total Alkalinity (TA): Remove very low values close to zero
    # Values below 2000 μeq/kg are likely measurement errors for seawater
    df.loc[df['ta'] < 2000, 'ta'] = np.nan

    return df


@st.cache_data
def load_raw_data():
    """
    Load oceanographic data from CSV file WITHOUT outlier removal.

    This function is used for outlier analysis visualizations where we want to
    show the full distribution including extreme values.

    Returns:
    --------
    pd.DataFrame
        Dataframe with all original values (no outlier removal)
    """
    # Read the prepared CSV file without removing outliers
    df = pd.read_csv('data/dichosocean_prepared.csv')

    # Rename columns to match the app's expected format
    df = df.rename(columns={
        'DateTime (UTC+00:00)': 'datetime',
        'Temperature (ºC)': 'temperature',
        'Pressure (dbar)': 'pressure',
        'Chlorophyll (ug/L)': 'chlorophyll_a',
        'Turbidity (NTU)': 'turbidity',
        'Salinity (PSU)': 'salinity',
        'pH': 'ph',
        'OD umolKg-1': 'dissolved_oxygen',
        'pCO2': 'pco2',
        'TA (ueq/kg)': 'ta'
    })

    # Convert datetime column to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])

    return df


# =============================================================================
# LOAD DATA INTO MEMORY
# =============================================================================
# Load both cleaned (with outliers removed) and raw (with all values) datasets
# The @st.cache_data decorator ensures data is only loaded once and cached in memory
data = load_data()          # Cleaned data for most visualizations
raw_data = load_raw_data()  # Raw data for outlier analysis

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

# Display project logos at the top of the sidebar
st.sidebar.image("resources/logodichoso2.png", use_container_width=True)  # DICHOSO project logo
st.sidebar.image("resources/logoicman.png", use_container_width=True)     # ICMAN-CSIC logo

# Add spacing after logos
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Define navigation menu options
# Each option corresponds to a different dashboard/analysis section
menu_options = [
    "❄️ About DICHOSOcean",      # Introduction and overview
    "📈 Data Overview",            # Data exploration and distribution
    "📊 Statistical Analysis",     # Correlation and statistical tests
    "📅 Interannual Variability",  # Year-to-year comparison (2024 vs 2025)
    "🐧 DICHOSO project",          # Project information and team
    "📚 References"                # Scientific references and papers
]

# Initialize session state for selected section
# This persists the user's selection across app reruns
if 'selected_section' not in st.session_state:
    st.session_state.selected_section = menu_options[0]  # Default to first option

# Create navigation buttons in the sidebar
st.sidebar.markdown("### Navigation")
for option in menu_options:
    # When a button is clicked, update the session state
    if st.sidebar.button(option, key=option, use_container_width=True):
        st.session_state.selected_section = option

# Get the currently selected section from session state
selected_section = st.session_state.selected_section

# =============================================================================
# DATE RANGE FILTER
# =============================================================================
# Allow users to filter data by selecting a custom date range
st.sidebar.markdown("### 📅 Time Range")
date_range = st.sidebar.date_input(
    "Select date range",
    value=(data['datetime'].min().date(), data['datetime'].max().date()),  # Default to full range
    min_value=data['datetime'].min().date(),  # Minimum selectable date
    max_value=data['datetime'].max().date()   # Maximum selectable date
)

# =============================================================================
# DEVELOPER INFORMATION (SIDEBAR)
# =============================================================================
# Display developer information and social links at the bottom of sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <p style="margin-bottom: 0.5rem; font-size: 0.9em; font-weight: bold;">Developed by: Alejandro Román</p>
    <div style="display: flex; justify-content: center; gap: 1rem; align-items: center;">
        <!-- LinkedIn profile link -->
        <a href="https://www.linkedin.com/in/alejandro-rom%C3%A1n-v%C3%A1zquez/" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30" height="30" alt="LinkedIn">
        </a>
        <!-- GitHub profile link -->
        <a href="https://github.com/alrova96" target="_blank">
            <img src="https://img.icons8.com/ios-filled/50/E9D8A6/github.png" width="30" height="30" alt="GitHub">
        </a>
        <!-- ORCID researcher ID link -->
        <a href="https://orcid.org/0000-0002-8868-9302" target="_blank">
            <img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_64x64.png" width="30" height="30" alt="ORCID">
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# DATA FILTERING BY DATE RANGE
# =============================================================================
# Apply the user-selected date range filter to both datasets
if len(date_range) == 2:
    # User has selected both start and end dates
    filtered_data = data[
        (data['datetime'].dt.date >= date_range[0]) &
        (data['datetime'].dt.date <= date_range[1])
    ]
    filtered_raw_data = raw_data[
        (raw_data['datetime'].dt.date >= date_range[0]) &
        (raw_data['datetime'].dt.date <= date_range[1])
    ]
else:
    # If only one date is selected or none, use full dataset
    filtered_data = data
    filtered_raw_data = raw_data

# =============================================================================
# MAIN CONTENT AREA - SECTION ROUTING
# =============================================================================
# Based on the selected navigation option, display the corresponding dashboard
# Each if/elif block handles a different section of the application

# -----------------------------------------------------------------------------
# SECTION 1: About DICHOSOcean
# -----------------------------------------------------------------------------
if selected_section == "❄️ About DICHOSOcean":
    # =============================================================================
    # This section provides an overview of the DICHOSOcean platform with:
    # - Video header with autoplay background footage
    # - Logo overlay with project name
    # - Key metrics cards showing dataset statistics
    # - Side-by-side comparison plots of variables for 2024 vs 2025
    # =============================================================================

    # -----------------------------------------------------------------------------
    # Video Header with Custom Styling
    # -----------------------------------------------------------------------------
    # Custom CSS to hide video controls and set video container dimensions
    st.markdown("""
    <style>
        /* Hide all video player controls to create clean background effect */
        div[data-testid="stVideo"] video::-webkit-media-controls {
            display: none !important;
        }
        div[data-testid="stVideo"] video::-webkit-media-controls-enclosure {
            display: none !important;
        }
        /* Disable pointer events to prevent user interaction with video */
        div[data-testid="stVideo"] video {
            pointer-events: none;
        }

        /* Set fixed height for video container */
        div[data-testid="stVideo"] {
            overflow: hidden;
            height: 300px !important;
        }
        /* Configure video to cover full container while maintaining aspect ratio */
        div[data-testid="stVideo"] video {
            width: 100% !important;
            height: 300px !important;
            object-fit: cover !important;  /* Crop video to fill container */
            object-position: center center !important;  /* Center video content */
        }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # Display Background Video
    # -----------------------------------------------------------------------------
    # Load and display video file showing oceanographic mooring deployment
    video_file = open('resources/fondeos.mp4', 'rb')
    video_bytes = video_file.read()
    # Video loops continuously, autoplays, and is muted for better UX
    st.video(video_bytes, loop=True, autoplay=True, muted=True)
    video_file.close()

    # -----------------------------------------------------------------------------
    # Logo and Title Overlay
    # -----------------------------------------------------------------------------
    # Import base64 module for encoding images to embed in HTML
    import base64

    # Read and encode DICHOSO logo as base64 string for HTML embedding
    logo_file = open('resources/logodichoso2.png', 'rb')
    logo_bytes = logo_file.read()
    logo_base64 = base64.b64encode(logo_bytes).decode()
    logo_file.close()

    st.markdown(f"""
    <div style="margin-top: -300px; position: relative; z-index: 10; pointer-events: none; height: 300px; display: flex; align-items: center; justify-content: center; margin-bottom: 2rem;">
        <div style="text-align: center; width: 90%;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 1rem;">
                <img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-right: 5px;" alt="DICHOSO">
                <span style="color: white; font-size: 3em; font-weight: bold; text-shadow: 3px 3px 6px rgba(0,0,0,0.8);">cean</span>
            </div>
            <p style="color: white; font-size: 1.2em; margin: 0 auto; max-width: 800px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                Analysis platform for data captured by biogeochemical sensors deployed in the Antarctic DICHOSO project during 2024 and 2025
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    # Count main oceanographic variables (7 core variables)
    num_variables = 7

    # Metric card base style (without border-left)
    metric_style_base = """
        background: #E9D8A6;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    """

    with col1:
        st.markdown(f"""
        <div style="{metric_style_base} border-left: 4px solid {CHART_COLORS[0]};">
            <h3 style="color: #001219; margin: 0; text-align: center; font-size: 1.1em;">📊 Observations</h3>
            <h2 style="color: #9B2226; margin: 0.5rem 0; text-align: center; font-size: 2.2em;">{len(filtered_data):,}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="{metric_style_base} border-left: 4px solid {CHART_COLORS[3]};">
            <h3 style="color: #001219; margin: 0; text-align: center; font-size: 1.1em;">🔬 Variables</h3>
            <h2 style="color: #9B2226; margin: 0.5rem 0; text-align: center; font-size: 2.2em;">{num_variables}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        start_year = filtered_data['datetime'].min().year
        end_year = filtered_data['datetime'].max().year
        st.markdown(f"""
        <div style="{metric_style_base} border-left: 4px solid {CHART_COLORS[5]};">
            <h3 style="color: #001219; margin: 0; text-align: center; font-size: 1.1em;">📅 Temporal Coverage</h3>
            <h2 style="color: #9B2226; margin: 0.5rem 0; text-align: center; font-size: 2.2em;">{start_year}-{end_year}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="{metric_style_base} border-left: 4px solid {CHART_COLORS[8]};">
            <h3 style="color: #001219; margin: 0; text-align: center; font-size: 1.1em;">⏱️ Temporal Frequency</h3>
            <h2 style="color: #9B2226; margin: 0.5rem 0; text-align: center; font-size: 2.2em;">10 min</h2>
        </div>
        """, unsafe_allow_html=True)

    # Individual variable plots by year (January-February only)
    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 2rem 0 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">📊 Variable Comparison: 2024 vs 2025</h2>
    </div>
    """, unsafe_allow_html=True)

    # Filter data for January and February only
    data_jan_feb = data[(data['datetime'].dt.month == 1) | (data['datetime'].dt.month == 2)]
    data_2024 = data_jan_feb[data_jan_feb['datetime'].dt.year == 2024].copy()
    data_2025 = data_jan_feb[data_jan_feb['datetime'].dt.year == 2025].copy()

    # Create common x-axis: convert 2025 dates to 2024 for true superposition
    # This makes both datasets share the exact same datetime values on x-axis
    data_2024['x_axis'] = data_2024['datetime']
    data_2025['x_axis'] = pd.to_datetime(data_2025['datetime'].dt.strftime('2024-%m-%d %H:%M:%S'))

    # Variables to plot
    variables = {
        'temperature': 'Temperature (°C)',
        'pressure': 'Pressure (dbar)',
        'salinity': 'Salinity (PSU)',
        'chlorophyll_a': 'Chlorophyll-a (μg/L)',
        'turbidity': 'Turbidity (NTU)',
        'ph': 'pH',
        'dissolved_oxygen': 'Dissolved Oxygen (μmol/kg)',
        'pco2': 'pCO2 (μatm)',
        'ta': 'TA (μeq/kg)'
    }

    # Create plots in single column layout - separate plots for each year
    for var_name, var_label in variables.items():
        # Title for the variable (centered)
        st.markdown(f"<h3 style='text-align: center;'>{var_label}</h3>", unsafe_allow_html=True)

        # Create two columns for 2024 and 2025
        col1, col2 = st.columns(2)

        with col1:
            # 2024 plot
            fig_2024 = go.Figure()
            fig_2024.add_trace(go.Scatter(
                x=data_2024['x_axis'],
                y=data_2024[var_name],
                mode='markers',
                name='2024',
                marker=dict(color='#9B2226', size=3, opacity=0.7)
            ))

            fig_2024.update_layout(
                title=dict(
                    text='2024',
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="Date",
                yaxis_title=var_label,
                plot_bgcolor='white',
                height=300,
                showlegend=False,
                xaxis=dict(
                    tickformat='%b %d'
                )
            )

            st.plotly_chart(fig_2024, use_container_width=True)

        with col2:
            # 2025 plot
            fig_2025 = go.Figure()
            fig_2025.add_trace(go.Scatter(
                x=data_2025['x_axis'],
                y=data_2025[var_name],
                mode='markers',
                name='2025',
                marker=dict(color='#EE9B00', size=3, opacity=0.7)
            ))

            fig_2025.update_layout(
                title=dict(
                    text='2025',
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title="Date",
                yaxis_title=var_label,
                plot_bgcolor='white',
                height=300,
                showlegend=False,
                xaxis=dict(
                    tickformat='%b %d'
                )
            )

            st.plotly_chart(fig_2025, use_container_width=True)

elif selected_section == "📈 Data Overview":
    # Custom header with Dataoverview image
    import base64

    # Read and encode Dataoverview image
    try:
        with open('resources/Dataoverview.JPG', 'rb') as img_file:
            dataoverview_base64 = base64.b64encode(img_file.read()).decode()
    except:
        dataoverview_base64 = ""

    st.markdown(f"""
    <div style="position: relative; width: 100%; height: 300px; overflow: hidden; border-radius: 8px;">
        <img src="data:image/jpeg;base64,{dataoverview_base64}" style="width: 100%; height: 300px; object-fit: cover; object-position: center;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">📈 Data Overview</h2>
    </div>
    """, unsafe_allow_html=True)

    # Data Display section
    st.markdown("<h3 style='text-align: center; font-weight: bold;'>Data Display</h3>", unsafe_allow_html=True)

    # Show first few rows of the data
    display_data = filtered_data[['datetime', 'temperature', 'pressure', 'salinity', 'chlorophyll_a', 'turbidity', 'ph', 'dissolved_oxygen', 'pco2', 'ta']].head(10)
    st.dataframe(display_data, use_container_width=True)

    # Two column layout for charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='text-align: center; font-weight: bold;'>Variable Distribution</h3>", unsafe_allow_html=True)

        # Calculate percentage of non-null data for each variable
        variables = ['temperature', 'pressure', 'salinity', 'chlorophyll_a', 'turbidity', 'ph', 'dissolved_oxygen', 'pco2', 'ta']
        var_counts = []
        var_labels = []

        for var in variables:
            count = filtered_data[var].notna().sum()
            var_counts.append(count)
            var_labels.append(var.replace('_', ' ').title())

        # Pie chart showing distribution of data points across variables
        fig = go.Figure(data=[go.Pie(
            labels=var_labels,
            values=var_counts,
            marker=dict(colors=CHART_COLORS[:len(variables)]),
            textinfo='percent',
            hovertemplate='%{label}<br>%{value} observations<br>%{percent}<extra></extra>',
            hole=0.3
        )])

        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h3 style='text-align: center; font-weight: bold;'>Outliers Analysis</h3>", unsafe_allow_html=True)

        # Box plot showing outliers for each variable (using raw data without outlier removal)
        fig = go.Figure()

        for i, var in enumerate(variables):
            fig.add_trace(go.Box(
                y=filtered_raw_data[var],
                name=var.replace('_', ' ').title(),
                marker_color=CHART_COLORS[i % len(CHART_COLORS)],
                boxmean='sd'
            ))

        fig.update_layout(
            height=500,
            yaxis_title="Value",
            showlegend=False,
            plot_bgcolor='white',
            xaxis={'tickangle': -45}
        )

        st.plotly_chart(fig, use_container_width=True)

    # Outlier percentage section
    st.markdown("<h3 style='text-align: center; font-weight: bold;'>Outlier Percentage by Variable</h3>", unsafe_allow_html=True)

    # Calculate outlier percentage for each variable using IQR method
    outlier_percentages = []
    outlier_counts = []
    var_labels_sorted = []

    for var in variables:
        # Get non-null values
        values = filtered_raw_data[var].dropna()

        if len(values) > 0:
            # Calculate IQR
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1

            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Count outliers
            outliers_count = ((values < lower_bound) | (values > upper_bound)).sum()
            outlier_pct = (outliers_count / len(values)) * 100

            outlier_percentages.append(outlier_pct)
            outlier_counts.append(outliers_count)
            var_labels_sorted.append(var.replace('_', ' ').title())
        else:
            outlier_percentages.append(0)
            outlier_counts.append(0)
            var_labels_sorted.append(var.replace('_', ' ').title())

    # Sort by percentage (descending) - highest at top
    sorted_data = sorted(zip(outlier_percentages, outlier_counts, var_labels_sorted), reverse=True)
    outlier_percentages_sorted = [x[0] for x in sorted_data]
    outlier_counts_sorted = [x[1] for x in sorted_data]
    var_labels_sorted = [x[2] for x in sorted_data]

    # Assign colors: warm colors (reds/oranges) for high percentages, cool colors (blues/greens) for low
    # CHART_COLORS order: blues (cool) to reds (warm)
    color_map = []
    n_vars = len(outlier_percentages_sorted)

    # Reverse CHART_COLORS so warm colors come first
    warm_to_cool_colors = CHART_COLORS[::-1]

    for i in range(n_vars):
        color_map.append(warm_to_cool_colors[i % len(warm_to_cool_colors)])

    # Create horizontal bar chart
    fig = go.Figure(data=[go.Bar(
        y=var_labels_sorted[::-1],  # Reverse to show highest at top
        x=outlier_percentages_sorted[::-1],
        orientation='h',
        marker=dict(color=color_map[::-1]),
        text=[f'{pct:.1f}% (n={count})' for pct, count in zip(outlier_percentages_sorted[::-1], outlier_counts_sorted[::-1])],
        textposition='outside',
        width=0.85  # Make bars thicker
    )])

    fig.update_layout(
        height=400,
        xaxis_title="Outlier Percentage (%)",
        yaxis_title="Variable",
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(
            range=[0, max(outlier_percentages_sorted) * 1.2]  # Add space for text outside bars
        )
    )

    st.plotly_chart(fig, use_container_width=True)

elif selected_section == "📊 Statistical Analysis":
    # Custom header with statistics image
    import base64

    # Read and encode statistics image
    try:
        with open('resources/statistics.jpg', 'rb') as img_file:
            statistics_base64 = base64.b64encode(img_file.read()).decode()
    except:
        statistics_base64 = ""

    st.markdown(f"""
    <div style="position: relative; width: 100%; height: 300px; overflow: hidden; border-radius: 8px;">
        <img src="data:image/jpeg;base64,{statistics_base64}" style="width: 100%; height: 300px; object-fit: cover; object-position: center;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">📊 Statistical Analysis</h2>
    </div>
    """, unsafe_allow_html=True)

    # Prepare data for correlation analysis
    from scipy.stats import pearsonr
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    variables = ['temperature', 'pressure', 'salinity', 'chlorophyll_a', 'turbidity', 'ph', 'dissolved_oxygen', 'pco2', 'ta']
    var_labels = [var.replace('_', ' ').title() for var in variables]

    # Calculate Pearson correlation matrix and p-values
    corr_matrix = filtered_data[variables].corr()
    n = len(filtered_data[variables])

    # Calculate p-values matrix
    p_values = np.zeros((len(variables), len(variables)))
    for i in range(len(variables)):
        for j in range(len(variables)):
            if i != j:
                valid_data = filtered_data[[variables[i], variables[j]]].dropna()
                if len(valid_data) > 2:
                    _, p_val = pearsonr(valid_data[variables[i]], valid_data[variables[j]])
                    p_values[i, j] = p_val
                else:
                    p_values[i, j] = 1.0
            else:
                p_values[i, j] = 0.0

    # Top row: Correlation matrix and p-values
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='text-align: center; font-weight: bold;'>Variable Correlation Matrix</h3>", unsafe_allow_html=True)

        # Use absolute value of correlation matrix
        corr_abs = np.abs(corr_matrix.values)

        # Custom colorscale: cool colors (blues) for low correlation, warm colors (reds) for high correlation
        # Correlation ranges from 0 to 1 (absolute value)
        colorscale = [
            [0.0, CHART_COLORS[0]],   # 0: dark blue (cold - no correlation)
            [0.25, CHART_COLORS[2]],  # 0.25: light blue
            [0.5, CHART_COLORS[4]],   # 0.5: beige
            [0.75, CHART_COLORS[6]],  # 0.75: orange
            [1.0, CHART_COLORS[9]]    # 1: red (warm - strong correlation)
        ]

        fig = go.Figure(data=go.Heatmap(
            z=corr_abs,
            x=var_labels,
            y=var_labels,
            colorscale=colorscale,
            zmin=0,
            zmax=1,
            text=np.round(corr_matrix.values, 2),  # Show original values (with sign)
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="|Correlation|")
        ))

        fig.update_layout(
            height=500,
            xaxis={'tickangle': -45},
            yaxis={'autorange': 'reversed'}
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h3 style='text-align: center; font-weight: bold;'>Statistical Significance</h3>", unsafe_allow_html=True)

        # Convert p-values to binary: 1 if p < 0.05 (significant), 0 if p >= 0.05 (not significant)
        significance_matrix = np.zeros((len(variables), len(variables)))
        for i in range(len(variables)):
            for j in range(len(variables)):
                if i == j:
                    significance_matrix[i, j] = np.nan  # Diagonal: self-correlation
                elif p_values[i, j] < 0.05:
                    significance_matrix[i, j] = 1  # Significant: warm color
                else:
                    significance_matrix[i, j] = 0  # Not significant: cool color

        # Custom colorscale: 0 = cool (blue), 1 = warm (red)
        colorscale_pval = [
            [0.0, CHART_COLORS[0]],   # Not significant: dark blue (cold)
            [1.0, CHART_COLORS[9]]    # Significant: red (warm)
        ]

        # Create text labels showing actual p-values
        text_labels = []
        for i in range(len(variables)):
            row_labels = []
            for j in range(len(variables)):
                if i == j:
                    row_labels.append('-')
                else:
                    row_labels.append(f'{p_values[i, j]:.3f}')
            text_labels.append(row_labels)

        fig = go.Figure(data=go.Heatmap(
            z=significance_matrix,
            x=var_labels,
            y=var_labels,
            colorscale=colorscale_pval,
            zmin=0,
            zmax=1,
            text=text_labels,
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(
                title="Significant",
                tickvals=[0, 1],
                ticktext=['No', 'Yes']
            )
        ))

        fig.update_layout(
            height=500,
            xaxis={'tickangle': -45},
            yaxis={'autorange': 'reversed'}
        )

        st.plotly_chart(fig, use_container_width=True)

    # Bottom: Best correlated variables
    st.markdown("<h3 style='text-align: center; font-weight: bold;'>Best correlated variables R² > 0.80 & p-value < 0.05</h3>", unsafe_allow_html=True)

    # Find pairs of variables with |R| > 0.894 (R² > 0.8) and p-value < 0.05
    # R² = 0.8 means |R| = sqrt(0.8) ≈ 0.894
    threshold_r = np.sqrt(0.8)
    best_pairs = []

    for i in range(len(variables)):
        for j in range(i+1, len(variables)):  # Only upper triangle to avoid duplicates
            r_val = corr_matrix.values[i, j]
            p_val = p_values[i, j]

            if abs(r_val) > threshold_r and p_val < 0.05:
                best_pairs.append({
                    'var1': variables[i],
                    'var2': variables[j],
                    'var1_label': var_labels[i],
                    'var2_label': var_labels[j],
                    'r': r_val,
                    'r2': r_val**2,
                    'p': p_val
                })

    # Sort by R² (descending) and take top 6
    best_pairs = sorted(best_pairs, key=lambda x: x['r2'], reverse=True)[:6]

    if len(best_pairs) > 0:
        # Create 2 rows with 3 columns each
        for row_idx in range(2):
            cols = st.columns(3)

            for col_idx in range(3):
                pair_idx = row_idx * 3 + col_idx

                if pair_idx < len(best_pairs):
                    pair = best_pairs[pair_idx]

                    with cols[col_idx]:
                        # Create scatter plot
                        fig = go.Figure()

                        # Get valid data (non-null for both variables)
                        valid_data = filtered_data[[pair['var1'], pair['var2']]].dropna()

                        fig.add_trace(go.Scatter(
                            x=valid_data[pair['var1']],
                            y=valid_data[pair['var2']],
                            mode='markers',
                            marker=dict(
                                color='#005F73',
                                size=4,
                                opacity=0.6
                            ),
                            name='Data'
                        ))

                        # Add regression line and equation
                        if len(valid_data) > 0:
                            z = np.polyfit(valid_data[pair['var1']], valid_data[pair['var2']], 1)
                            slope, intercept = z[0], z[1]
                            p = np.poly1d(z)
                            x_line = np.linspace(valid_data[pair['var1']].min(), valid_data[pair['var1']].max(), 100)
                            y_line = p(x_line)

                            fig.add_trace(go.Scatter(
                                x=x_line,
                                y=y_line,
                                mode='lines',
                                line=dict(color='#EE9B00', width=2),
                                name='Fit'
                            ))

                            # Add equation as annotation
                            equation_text = f"y = {slope:.3f}x + {intercept:.3f}<br>R² = {pair['r2']:.3f}"
                            fig.add_annotation(
                                x=0.05,
                                y=0.95,
                                xref='paper',
                                yref='paper',
                                text=equation_text,
                                showarrow=False,
                                bgcolor='rgba(255, 255, 255, 0.8)',
                                bordercolor='#005F73',
                                borderwidth=1,
                                font=dict(size=10)
                            )

                        fig.update_layout(
                            title=dict(
                                text=f"{pair['var1_label']} vs {pair['var2_label']}",
                                x=0.5,
                                xanchor='center',
                                font=dict(size=13)
                            ),
                            xaxis_title=pair['var1_label'],
                            yaxis_title=pair['var2_label'],
                            height=350,
                            showlegend=False,
                            plot_bgcolor='white',
                            margin=dict(t=40, b=60, l=60, r=20)
                        )

                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No variable pairs found with R² > 0.80 and p-value < 0.05")

elif selected_section == "📅 Interannual Variability":
    # Custom header with interannual image
    import base64

    # Read and encode interannual image
    try:
        with open('resources/interannual.jpg', 'rb') as img_file:
            interannual_base64 = base64.b64encode(img_file.read()).decode()
    except:
        interannual_base64 = ""

    st.markdown(f"""
    <div style="position: relative; width: 100%; height: 300px; overflow: hidden; border-radius: 8px;">
        <img src="data:image/jpeg;base64,{interannual_base64}" style="width: 100%; height: 300px; object-fit: cover; object-position: center;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">📅 Interannual Variability</h2>
    </div>
    """, unsafe_allow_html=True)

    # Interannual variability analysis - comparing 2024 vs 2025
    # Using cleaned dataset (data variable has outliers removed)
    from scipy.stats import mannwhitneyu, ttest_ind

    variables_to_plot = ['temperature', 'pressure', 'salinity', 'chlorophyll_a', 'turbidity', 'ph', 'dissolved_oxygen', 'pco2', 'ta']
    var_labels_dict = {
        'temperature': 'Temperature',
        'pressure': 'Pressure',
        'salinity': 'Salinity',
        'chlorophyll_a': 'Chlorophyll-a',
        'turbidity': 'Turbidity',
        'ph': 'pH',
        'dissolved_oxygen': 'Dissolved Oxygen',
        'pco2': 'pCO2',
        'ta': 'TA'
    }

    # Create summary data for text at the end
    summary_data = []

    # Create plots for each variable - 3 columns (Box plot, Monthly trends, Histogram)
    for var in variables_to_plot:
        st.markdown(f"<h3 style='text-align: center; font-weight: bold; margin-top: 2rem;'>{var_labels_dict[var]}</h3>", unsafe_allow_html=True)

        # Get data for both years
        data_2024 = data[data['datetime'].dt.year == 2024][var].dropna()
        data_2025 = data[data['datetime'].dt.year == 2025][var].dropna()

        col1, col2, col3 = st.columns(3)

        with col1:
            # Box plot for distribution comparison
            fig_box = go.Figure()

            fig_box.add_trace(go.Box(
                y=data_2024,
                name='2024',
                marker_color='#005F73',
                boxmean='sd'
            ))

            fig_box.add_trace(go.Box(
                y=data_2025,
                name='2025',
                marker_color='#EE9B00',
                boxmean='sd'
            ))

            fig_box.update_layout(
                title=dict(text='Distribution Comparison', x=0.5, xanchor='center', font=dict(size=12)),
                yaxis_title=var_labels_dict[var],
                height=350,
                plot_bgcolor='white',
                showlegend=True
            )

            st.plotly_chart(fig_box, use_container_width=True)

        with col2:
            # Monthly time series comparison
            fig_monthly = go.Figure()

            # Add month column if not exists
            data_with_month_2024 = data[data['datetime'].dt.year == 2024].copy()
            data_with_month_2024['month'] = data_with_month_2024['datetime'].dt.month
            monthly_2024 = data_with_month_2024.groupby('month')[var].mean()

            data_with_month_2025 = data[data['datetime'].dt.year == 2025].copy()
            data_with_month_2025['month'] = data_with_month_2025['datetime'].dt.month
            monthly_2025 = data_with_month_2025.groupby('month')[var].mean()

            fig_monthly.add_trace(go.Scatter(
                x=monthly_2024.index,
                y=monthly_2024.values,
                mode='lines+markers',
                name='2024',
                line=dict(color='#005F73', width=2),
                marker=dict(size=8)
            ))

            fig_monthly.add_trace(go.Scatter(
                x=monthly_2025.index,
                y=monthly_2025.values,
                mode='lines+markers',
                name='2025',
                line=dict(color='#EE9B00', width=2),
                marker=dict(size=8, symbol='square')
            ))

            fig_monthly.update_layout(
                title=dict(text='Monthly Trends', x=0.5, xanchor='center', font=dict(size=12)),
                xaxis_title='Month',
                yaxis_title=f'Mean {var_labels_dict[var]}',
                height=350,
                plot_bgcolor='white',
                showlegend=True,
                xaxis=dict(tickmode='linear', tick0=1, dtick=1)
            )

            st.plotly_chart(fig_monthly, use_container_width=True)

        with col3:
            # Histogram comparison
            fig_hist = go.Figure()

            # Calculate bins
            combined_data = pd.concat([data_2024, data_2025])
            bins = np.linspace(combined_data.min(), combined_data.max(), 30)

            fig_hist.add_trace(go.Histogram(
                x=data_2024,
                name='2024',
                marker_color='#005F73',
                opacity=0.6,
                xbins=dict(start=bins[0], end=bins[-1], size=(bins[-1]-bins[0])/30),
                histnorm='probability density'
            ))

            fig_hist.add_trace(go.Histogram(
                x=data_2025,
                name='2025',
                marker_color='#EE9B00',
                opacity=0.6,
                xbins=dict(start=bins[0], end=bins[-1], size=(bins[-1]-bins[0])/30),
                histnorm='probability density'
            ))

            # Statistical tests
            try:
                mw_stat, mw_p = mannwhitneyu(data_2024, data_2025, alternative='two-sided')
                mw_result = f"Mann-Whitney U: p={mw_p:.4f}"
            except:
                mw_result = "Mann-Whitney U: N/A"
                mw_p = np.nan

            try:
                t_stat, t_p = ttest_ind(data_2024, data_2025)
                t_result = f"T-test: p={t_p:.4f}"
            except:
                t_result = "T-test: N/A"
                t_p = np.nan

            test_text = f"{mw_result}<br>{t_result}"

            fig_hist.add_annotation(
                x=0.02,
                y=0.98,
                xref='paper',
                yref='paper',
                text=test_text,
                showarrow=False,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#005F73',
                borderwidth=1,
                font=dict(size=9),
                xanchor='left',
                yanchor='top'
            )

            fig_hist.update_layout(
                title=dict(text='Frequency Distribution', x=0.5, xanchor='center', font=dict(size=12)),
                xaxis_title=var_labels_dict[var],
                yaxis_title='Density',
                height=350,
                plot_bgcolor='white',
                showlegend=True,
                barmode='overlay'
            )

            st.plotly_chart(fig_hist, use_container_width=True)

        # Calculate statistics for summary
        mean_2024 = data_2024.mean()
        mean_2025 = data_2025.mean()
        pct_change = ((mean_2025 - mean_2024) / mean_2024) * 100 if mean_2024 != 0 else np.inf
        significance = "Significant" if mw_p < 0.05 else "Not Significant"

        summary_data.append({
            'Variable': var_labels_dict[var],
            'Mean_2024': mean_2024,
            'Mean_2025': mean_2025,
            'Pct_Change': pct_change,
            'Significance': significance,
            'P_Value': mw_p
        })

    # Add summary section at the end
    st.markdown("<h3 style='text-align: center; font-weight: bold; margin-top: 3rem;'>📊 Interannual Comparison Summary</h3>", unsafe_allow_html=True)

    # Create summary table
    summary_df = pd.DataFrame(summary_data)
    summary_df['Mean_2024'] = summary_df['Mean_2024'].round(3)
    summary_df['Mean_2025'] = summary_df['Mean_2025'].round(3)
    summary_df['Pct_Change'] = summary_df['Pct_Change'].round(1)

    st.dataframe(summary_df[['Variable', 'Mean_2024', 'Mean_2025', 'Pct_Change', 'Significance']], use_container_width=True)

    # Highlight significant changes
    significant_changes = [row for row in summary_data if row['P_Value'] < 0.05 and not np.isnan(row['P_Value'])]

    if significant_changes:
        st.markdown("<h4 style='text-align: center; font-size: 1em;'>🔍 Significant Changes Detected:</h4>", unsafe_allow_html=True)
        for change in significant_changes:
            direction = "↗️ Increase" if change['Pct_Change'] > 0 else "↘️ Decrease"
            st.markdown(f"- **{change['Variable']}**: {direction} of {abs(change['Pct_Change']):.1f}% (p={change['P_Value']:.4f})")
    else:
        st.success("✅ NO SIGNIFICANT INTERANNUAL CHANGES DETECTED")

    # Oceanographic implications
    st.markdown("<h4 style='text-align: center; font-size: 1em; margin-top: 2rem;'>🌊 Oceanographic Implications:</h4>", unsafe_allow_html=True)
    st.markdown("""
    - Interannual variability analysis reveals ecosystem stability/changes
    - Significant changes may indicate environmental shifts or seasonal patterns
    - Statistical testing provides confidence in observed differences
    - Multiple visualization approaches enhance pattern detection
    """)

elif selected_section == "🐧 DICHOSO project":
    # Custom header with hesperides image and logo overlay
    import base64

    # Read and encode hesperides image
    try:
        with open('resources/hesperides.jpeg', 'rb') as img_file:
            hesperides_base64 = base64.b64encode(img_file.read()).decode()
    except:
        hesperides_base64 = ""

    # Read and encode logo
    try:
        with open('resources/logodichoso2.png', 'rb') as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode()
    except:
        logo_base64 = ""

    st.markdown(f"""
    <div style="position: relative; width: 100%; height: 300px; overflow: hidden; border-radius: 8px;">
        <img src="data:image/jpeg;base64,{hesperides_base64}" style="width: 100%; height: 300px; object-fit: cover; object-position: center;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10;">
            <img src="data:image/png;base64,{logo_base64}" style="height: 150px; filter: drop-shadow(0 0 10px rgba(0,0,0,0.5));">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Project Leaders Section
    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 2rem 0 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">👥 Project Leaders</h2>
    </div>
    """, unsafe_allow_html=True)

    # Principal Investigators
    principal_investigators = [
        {"name": "Dr. I. Emma Huertas", "position": "Principal Investigator", "email": "emma.huertas@csic.es", "image": "huertas.jpeg"},
        {"name": "Dr. Antonio Tovar-Sánchez", "position": "Co-Principal Investigator", "email": "a.tovar@csic.es", "image": "tovar.jpeg"}
    ]

    cols = st.columns(2)
    for idx, pi in enumerate(principal_investigators):
        with cols[idx]:
            try:
                with open(f'resources/{pi["image"]}', 'rb') as img_file:
                    pi_img_base64 = base64.b64encode(img_file.read()).decode()
            except:
                pi_img_base64 = ""

            # Assign different colors from CHART_COLORS
            border_color = CHART_COLORS[1] if idx == 0 else CHART_COLORS[6]

            st.markdown(f"""
            <div style="background: #E9D8A6; padding: 1.5rem; border-radius: 8px; text-align: center; height: 100%; border-left: 4px solid {border_color};">
                <img src="data:image/jpeg;base64,{pi_img_base64}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem; border: 3px solid #022B3A;">
                <h4 style="color: #022B3A; margin: 0.5rem 0; font-weight: bold;">{pi['name']}</h4>
                <p style="color: #005F73; margin: 0.5rem 0; font-size: 0.9em; font-weight: 600;">{pi['position']}</p>
                <p style="color: #001219; margin: 0.5rem 0; font-size: 0.85em;">📧 {pi['email']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Project Objectives Section
    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 2rem 0 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">🎯 Project Objectives</h2>
    </div>
    """, unsafe_allow_html=True)

    objectives = [
        {
            "emoji": "🌊",
            "title": "Water Mass Characterization",
            "description": "Characterize the water masses of Deception Island and their contribution to biogeochemical inventories of the Southern Ocean."
        },
        {
            "emoji": "🔬",
            "title": "Biogeochemical Analysis",
            "description": "Evaluate concentrations of nutrients, trace metals, and greenhouse gases in the Antarctic region."
        },
        {
            "emoji": "📊",
            "title": "Current Balance and Future Trends",
            "description": "Determine the current balance and future trends of biogeochemical processes in the context of climate change."
        },
        {
            "emoji": "🧪",
            "title": "Hydrothermal Activity",
            "description": "Investigate the impact of hydrothermal activity on seawater chemistry and marine ecosystems."
        }
    ]

    col1, col2 = st.columns(2)
    # Define colors for objectives
    objective_colors = [CHART_COLORS[0], CHART_COLORS[3], CHART_COLORS[5], CHART_COLORS[8]]

    for idx, obj in enumerate(objectives):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"""
            <div style="background: #E9D8A6; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {objective_colors[idx]};">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 2em;">{obj['emoji']}</span>
                    <h4 style="color: #022B3A; margin: 0; font-weight: bold;">{obj['title']}</h4>
                </div>
                <p style="color: #001219; margin: 0; line-height: 1.5; text-align: justify;">{obj['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Main Activities Section
    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 2rem 0 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">⚙️ Main Activities</h2>
    </div>
    """, unsafe_allow_html=True)

    activities = [
        {
            "icon": "🚢",
            "title": "Oceanographic Campaigns",
            "description": "Conducting scientific expeditions aboard the Research Vessel Hespérides for water sample collection and in situ measurements in the Deception Island region.",
            "color": "#005F73",
            "image": "oceanographic.jpeg"
        },
        {
            "icon": "🔬",
            "title": "Laboratory Analysis",
            "description": "Determination of concentrations of inorganic nutrients, trace metals, pH, total alkalinity, pCO2, and greenhouse gases (CH4, N2O) at ICMAN-CSIC facilities.",
            "color": "#0A9396",
            "image": "laboratory.jpeg"
        },
        {
            "icon": "🛰️",
            "title": "Remote Sensing and Satellite Oceanography",
            "description": "Analysis of satellite data for studying chlorophyll-a, sea surface temperature, and detection of hydrothermal plumes using high-resolution imagery.",
            "color": "#94D2BD",
            "image": "remote.jpg"
        },
        {
            "icon": "💻",
            "title": "Modeling and Data Analysis",
            "description": "Development of biogeochemical models and advanced statistical analysis to evaluate temporal trends and future projections in the context of climate change.",
            "color": "#EE9B00",
            "image": "modeling.jpeg"
        },
        {
            "icon": "📚",
            "title": "Scientific Dissemination",
            "description": "Publication of results in high-impact scientific journals, presentations at international conferences, and communication with society about the importance of Antarctica.",
            "color": "#CA6702",
            "image": "science.jpg"
        }
    ]

    for idx, activity in enumerate(activities):
        # Read and encode activity image
        try:
            with open(f'resources/{activity["image"]}', 'rb') as img_file:
                activity_img_base64 = base64.b64encode(img_file.read()).decode()
        except:
            activity_img_base64 = ""

        # Alternate image position: left for even indices, right for odd indices
        if idx % 2 == 0:
            # Image on the left
            st.markdown(f"""
            <div style="background: #E9D8A6; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 6px solid {activity['color']};">
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <div style="flex-shrink: 0;">
                        <img src="data:image/jpeg;base64,{activity_img_base64}" style="width: 250px; height: 180px; object-fit: cover; border-radius: 8px;">
                    </div>
                    <div style="flex-grow: 1;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 2.5em;">{activity['icon']}</span>
                            <h3 style="color: #022B3A; margin: 0; font-weight: bold;">{activity['title']}</h3>
                        </div>
                        <p style="color: #001219; margin: 0; line-height: 1.6; text-align: justify; font-size: 0.95em;">{activity['description']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Image on the right
            st.markdown(f"""
            <div style="background: #E9D8A6; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 6px solid {activity['color']};">
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <div style="flex-grow: 1;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
                            <span style="font-size: 2.5em;">{activity['icon']}</span>
                            <h3 style="color: #022B3A; margin: 0; font-weight: bold;">{activity['title']}</h3>
                        </div>
                        <p style="color: #001219; margin: 0; line-height: 1.6; text-align: justify; font-size: 0.95em;">{activity['description']}</p>
                    </div>
                    <div style="flex-shrink: 0;">
                        <img src="data:image/jpeg;base64,{activity_img_base64}" style="width: 250px; height: 180px; object-fit: cover; border-radius: 8px;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif selected_section == "📚 References":
    st.markdown("""
    <div style="background: #1F7A8C; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #022B3A; margin: 1rem 0;">
        <h2 style="color: #E9D8A6; margin: 0; font-size: 1.3em;">📚 References</h2>
    </div>
    """, unsafe_allow_html=True)

    import base64

    # Paper data
    papers = [
        {
            "image": "paper_1.jpg",
            "title": "Changing Biogeochemistry of the Southern Ocean and Its Ecosystem Implications",
            "authors": "Sian F. Henley, Emma L. Cavan, Sarah E. Fawcett, Rodrigo Kerr, Thiago Monteiro, Robert M. Sherrell, Andrew R. Bowie, Philip W. Boyd, David K. A. Barnes, Irene R. Schloss, Tanya Marshall, Raquel Flynn, Shantelle Smith",
            "description": "The Southern Ocean plays a critical role in global climate as a major carbon dioxide sink and nutrient supplier to the global thermocline. Climate-mediated changes in Southern Ocean biogeochemistry are likely to impact primary production, sea-air CO2 exchange, and ecosystem functioning.",
            "url": "https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2020.00581/full",
            "doi": "10.3389/fmars.2020.00581",
            "journal": "Frontiers in Marine Science",
            "year": "2020"
        },
        {
            "image": "paper_2.jpg",
            "title": "Hydrothermal alteration of seawater biogeochemistry in Deception Island (South Shetland Islands, Antarctica)",
            "authors": "Oleg Belyaev, I. Emma Huertas, Gabriel Navarro, Silvia Amaya-Vías, Mercedes de la Paz, Erica Sparaventi, Sergio Heredia, Camila F. Sukekava, Luis M. Laglera, Antonio Tovar-Sánchez",
            "description": "This study examined trace metals and greenhouse gases in Port Foster, Deception Island, Antarctica, finding higher concentrations of trace metals in the northeastern bay region likely due to hydrothermal activity. The bay acted as a CO2 sink and a CH4 source.",
            "url": "https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2024.1432122/full",
            "doi": "10.3389/fmars.2024.1432122",
            "journal": "Frontiers in Marine Science",
            "year": "2024"
        },
        {
            "image": "paper_3.png",
            "title": "One-third of Southern Ocean productivity is supported by dust deposition",
            "authors": "Jakob Weis, Zanna Chase, Christina Schallenberg, Peter G. Strutton, Andrew R. Bowie, Sonya L. Fiddes",
            "description": "This study combined 11 years of nitrate observations from autonomous biogeochemical floats with Southern Hemisphere dust simulations to quantify the relationship between dust-iron deposition and annual net community production in the iron-limited Southern Ocean.",
            "url": "https://www.nature.com/articles/s41586-024-07366-4",
            "doi": "10.1038/s41586-024-07366-4",
            "journal": "Nature",
            "year": "2024"
        },
        {
            "image": "paper_4.png",
            "title": "Severe 21st-century ocean acidification in Antarctic Marine Protected Areas",
            "authors": "Cara Nissen, Nicole S. Lovenduski, Cassandra M. Brooks, Mario Hoppema, Ralph Timmermann, Judith Hauck",
            "description": "This study presents 21st-century projections of ocean acidification in Antarctic Marine Protected Areas under four emission scenarios. By 2100, the researchers project pH declines of up to 0.36 in the top 200 meters, with end-of-century aragonite undersaturation ubiquitous.",
            "url": "https://www.nature.com/articles/s41467-023-44438-x",
            "doi": "10.1038/s41467-023-44438-x",
            "journal": "Nature Communications",
            "year": "2024"
        },
        {
            "image": "paper_5.jpg",
            "title": "Antarctic Oceanography - Marine Environmental Research",
            "authors": "Multiple authors",
            "description": "This study examines oceanographic processes and environmental conditions in Antarctic waters, contributing to our understanding of the Southern Ocean ecosystem and its role in global climate systems.",
            "url": "https://www.sciencedirect.com/science/article/pii/S0141113618304380",
            "doi": "10.1016/S0141-1136(18)30438-0",
            "journal": "Marine Environmental Research",
            "year": "2018"
        },
        {
            "image": "paper_6.png",
            "title": "Southern Ocean Biogeochemistry and Circulation",
            "authors": "Multiple authors",
            "description": "This research investigates biogeochemical processes and ocean circulation patterns in the Southern Ocean, providing insights into nutrient dynamics and their impact on marine productivity.",
            "url": "https://www.sciencedirect.com/science/article/pii/S0967064503000869",
            "doi": "10.1016/S0967-0645(03)00086-9",
            "journal": "Deep Sea Research Part II",
            "year": "2003"
        },
        {
            "image": "paper_7.png",
            "title": "Choosing the future of Antarctica",
            "authors": "S. R. Rintoul, S. L. Chown, R. M. DeConto, M. H. England, H. A. Fricker, V. Masson-Delmotte, T. R. Naish, M. J. Siegert, J. C. Xavier",
            "description": "This paper examines future scenarios for Antarctica and discusses how decisions made in the coming decades will determine the continent's future. It assesses the effects of climate change on Antarctic ice sheets, ecosystems, and the Southern Ocean, emphasizing the need for international cooperation and evidence-based policy decisions.",
            "url": "https://www.nature.com/articles/s41586-018-0173-4",
            "doi": "10.1038/s41586-018-0173-4",
            "journal": "Nature",
            "year": "2018"
        },
        {
            "image": "paper_8.png",
            "title": "State of the Antarctic and Southern Ocean climate system",
            "authors": "P. A. Mayewski, M. P. Meredith, C. P. Summerhayes, J. Turner, A. Worby, P. J. Barrett, G. Casassa, N. A. N. Bertler, T. Bracegirdle, A. C. Naveira Garabato, D. Bromwich, H. Campbell, G. S. Hamilton, W. B. Lyons, K. A. Maasch, S. Aoki, C. Xiao, T. van Ommen",
            "description": "This comprehensive review examines developments in understanding the Antarctic and Southern Ocean climate system over recent millennia. The paper synthesizes knowledge about climate variability, ice sheet dynamics, and ocean circulation, providing insights into how these systems interact and influence global climate patterns.",
            "url": "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007RG000231",
            "doi": "10.1029/2007RG000231",
            "journal": "Reviews of Geophysics",
            "year": "2009"
        },
        {
            "image": "paper_9.jpg",
            "title": "Glacial greenhouse-gas fluctuations controlled by ocean circulation changes",
            "authors": "Andreas Schmittner, Eric D. Galbraith",
            "description": "This study presents model simulations demonstrating that changes in ocean circulation, particularly the Atlantic Meridional Overturning Circulation, were the primary driver of millennial-scale fluctuations in atmospheric carbon dioxide and nitrous oxide during glacial periods. The findings highlight the critical role of ocean dynamics in regulating Earth's climate through greenhouse gas concentrations.",
            "url": "https://www.nature.com/articles/nature07531",
            "doi": "10.1038/nature07531",
            "journal": "Nature",
            "year": "2008"
        }
    ]

    # Display each paper
    for idx, paper in enumerate(papers):
        # Read and encode paper image
        try:
            with open(f'resources/{paper["image"]}', 'rb') as img_file:
                paper_img_base64 = base64.b64encode(img_file.read()).decode()
        except:
            paper_img_base64 = ""

        # Assign color from CHART_COLORS (cycle through if more papers than colors)
        border_color = CHART_COLORS[idx % len(CHART_COLORS)]

        st.markdown(f"""
        <div style="background: #E9D8A6; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; display: flex; gap: 1.5rem; border-left: 4px solid {border_color};">
            <div style="flex-shrink: 0;">
                <img src="data:image/jpeg;base64,{paper_img_base64}" style="width: 200px; height: 250px; object-fit: cover; border-radius: 8px;">
            </div>
            <div style="flex-grow: 1;">
                <h3 style="color: #022B3A; margin-top: 0; margin-bottom: 0.5rem; font-weight: bold; text-align: justify;">{paper['title']}</h3>
                <p style="color: #9B2226; margin-bottom: 0.75rem; font-size: 0.95em; text-align: justify;">{paper['authors']}</p>
                <p style="color: #022B3A; margin-bottom: 1rem; line-height: 1.5; text-align: justify;">{paper['description']}</p>
                <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap; font-size: 0.9em;">
                    <span style="color: #005F73;"><strong>{paper['journal']}</strong> ({paper['year']})</span>
                    <a href="{paper['url']}" target="_blank" style="color: #005F73; text-decoration: none;">🌐 Full text</a>
                    <span style="color: #005F73;">DOI: {paper['doi']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1.5rem;">
    <p style="font-weight: bold; color: #001219; margin-bottom: 1rem; font-size: 1.1em;">Developed by Alejandro Román</p>
    <div style="display: flex; justify-content: center; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
        <a href="https://www.linkedin.com/in/alejandro-rom%C3%A1n-v%C3%A1zquez/" target="_blank" title="LinkedIn">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="35" height="35" alt="LinkedIn">
        </a>
        <a href="https://github.com/alrova96" target="_blank" title="GitHub">
            <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="35" height="35" alt="GitHub">
        </a>
        <a href="https://orcid.org/0000-0002-8868-9302" target="_blank" title="ORCID">
            <img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_64x64.png" width="35" height="35" alt="ORCID">
        </a>
        <a href="mailto:a.roman@csic.es" title="Email">
            <img src="https://cdn-icons-png.flaticon.com/512/561/561127.png" width="35" height="35" alt="Email">
        </a>
        <a href="https://alrova96.github.io/" target="_blank" title="Website">
            <img src="https://cdn-icons-png.flaticon.com/512/1006/1006771.png" width="35" height="35" alt="Website">
        </a>
        <a href="https://twitter.com/a_roman_4" target="_blank" title="X (Twitter)">
            <img src="https://cdn-icons-png.flaticon.com/512/5968/5968830.png" width="35" height="35" alt="X">
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

