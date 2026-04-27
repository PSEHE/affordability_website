# %%
"""
Generate static and interactive figures for the affordability website
Uses matplotlib for static figures and plotly for interactive visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pathlib import Path
import json
import os
try:
    import geopandas as gpd
except ImportError:
    gpd = None
    print("⚠ GeoPandas not installed. GHG emissions map will be skipped.")
# Set matplotlib style to match PSE brand colors
plt.style.use('seaborn-v0_8-darkgrid')

# PSE Brand Colors (matching frontend)
PSE_COLORS = {
    'forest_green': '#275258',
    'forest_green_light': '#3a6b72',
    'forest_green_lighter': '#e8f0f1',
    'orange': '#fb923c',
    'orange_light': '#fed7aa',
    'white': '#ffffff',
    'black': '#252728',
    'gray': '#6b7280',
    'light_blue': '#C4F2EB'
}


def normalize_colors(color_list):
    return [(r/255, g/255, b/255) for r, g, b in color_list]

list_colors_blacks = normalize_colors([(37,39,40),(110,110,110),(150,150,150),(196,195,198)])
list_colors_blues = normalize_colors([(33,76,111),(57,116,147),(123,171,190),(169,204,217)])
list_colors_reds = normalize_colors([(196,38,45),(240,76,59),(244,124,93),(249,172,141)])
list_colors_oranges = normalize_colors([(247,104,40),(247,135,30),(247,173,75),(255,206,107)])
list_colors_cyans = normalize_colors([(39,82,88),(0,167,158),(107,214,204),(196,242,235)])


# Set default matplotlib parameters
matplotlib.rcParams['font.family'] = 'Source Sans Pro'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['axes.titlesize'] = 16
matplotlib.rcParams['xtick.labelsize'] = 11
matplotlib.rcParams['ytick.labelsize'] = 11
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['figure.titlesize'] = 18

# Output directory
OUTPUT_DIR = Path(__file__).parent / 'assets'
OUTPUT_DIR.mkdir(exist_ok=True)
import pyarrow.parquet

def read_parquet_schema_df(uri: str) -> pd.DataFrame:
    """Return a Pandas dataframe corresponding to the schema of a local URI of a parquet file.

    The returned dataframe has the columns: column, pa_dtype
    """
    # Ref: https://stackoverflow.com/a/64288036/
    schema = pyarrow.parquet.read_schema(uri, memory_map=True)
    schema = pd.DataFrame(({"column": name, "pa_dtype": str(pa_dtype)} for name, pa_dtype in zip(schema.names, schema.types)))
    schema = schema.reindex(columns=["column", "pa_dtype"], fill_value=pd.NA)  # Ensures columns in case the parquet file has an empty dataframe.
    return schema
filepath_nation = os.path.join("..","affordability_data","household_energy_estimates_2024_11",   "nationwide_parquet","nationwide_household_data.parquet")
schema = read_parquet_schema_df(filepath_nation)
columns = schema['column'].tolist()
usecols = [col for col in columns if col.startswith("BTU") and (col.endswith("EL") or col.endswith("NG") or col.endswith("FO") or col.endswith("LP"))]
# %%
def save_figure(fig, filename, formats=['svg', 'webp', 'png'], dpi=300):
    """
    Save figure in multiple formats optimized for web
    
    Args:
        fig: matplotlib figure object
        filename: base filename (without extension)
        formats: list of formats to save
        dpi: resolution for raster formats
    """
    for fmt in formats:
        filepath = OUTPUT_DIR / f"{filename}.{fmt}"
        
        if fmt == 'svg':
            # SVG: Best for web, scalable, small file size
            fig.savefig(filepath, format='svg', bbox_inches='tight', 
                       transparent=True, dpi=dpi)
            print(f"✓ Saved {filepath} (SVG - recommended for web)")
            
        elif fmt == 'webp':
            # WebP: Modern format, excellent compression
            try:
                fig.savefig(filepath, format='webp', bbox_inches='tight', 
                           dpi=dpi)
                print(f"✓ Saved {filepath} (WebP - modern format)")
            except Exception as e:
                print(f"⚠ Could not save WebP format: {e}")
            
        elif fmt == 'png':
            # PNG: Fallback for older browsers
            fig.savefig(filepath, format='png', bbox_inches='tight', 
                       dpi=dpi, transparent=True)
            print(f"✓ Saved {filepath} (PNG - fallback)")
            
        else:
            fig.savefig(filepath, bbox_inches='tight', dpi=dpi)
            print(f"✓ Saved {filepath}")


def create_energy_costs_figure():
    """
    Figure 1: Total energy costs breakdown by end use and energy source
    Two-part figure: Left = Canva diagram placeholder, Right = Stacked bar chart
    """
    # Get column names from parquet file without loading entire file
    schema = read_parquet_schema_df(filepath_nation)
    columns = schema['column'].tolist()
    
    # Load all BTU and RATE columns
    btu_cols = [col for col in columns if col.startswith("BTU_")]
    rate_cols = ["RATE_EL", "RATE_NG", "RATE_FO", "RATE_LP"]
    usecols = btu_cols + rate_cols
    
    df = pd.read_parquet(filepath_nation, columns=usecols)
    
    # Add fan pump electric to cooling electric since it is always electric
    df["BTU_COL_EL"] = df["BTU_COL_EL"] + df["BTU_FANPUMP_EL"]
    df.drop(columns=["BTU_FANPUMP_EL"], inplace=True)
    
    # Calculate cost columns: multiply BTU by corresponding RATE
    # Rates are in $/MMBtu, so cost = BTU * RATE
    for fuel in ["EL", "NG", "FO", "LP"]:
        btu_cols_fuel = [col for col in df.columns if col.startswith("BTU_") and col.endswith(f"_{fuel}")]
        for btu_col in btu_cols_fuel:
            cost_col = btu_col.replace("BTU_", "COST_")
            df[cost_col] = df[btu_col] * df[f"RATE_{fuel}"]
    
    # Define end uses and energy sources
    end_uses = {
        'Water Heating': 'WATER',
        'Space Heating': 'SPH',
        'Space Cooling': 'COL',
        'Clothes Drying': 'DRYING',
        'Other Appliances': 'APP'
    }
    
    energy_sources = {
        'Electric': 'EL',
        'Methane Gas': 'NG',
        'Propane': 'LP',
        'Fuel Oil': 'FO'
    }
    
    # Source colors (using PSE palette extended with custom colors)
    source_colors = {
        'Electric': list_colors_oranges[0],  # Orange
        'Methane Gas': list_colors_cyans[1],  # Cyan
        'Propane': list_colors_blues[1],  # Blue
        'Fuel Oil': list_colors_blacks[1]  # Gray
    }
    
    # Aggregate costs by end use and energy source (sum across all households, convert to billions)
    cost_data = {}
    for end_use_name, end_use_code in end_uses.items():
        cost_data[end_use_name] = {}
        for source_name, source_code in energy_sources.items():
            cost_col = f"COST_{end_use_code}_{source_code}"
            if cost_col in df.columns:
                # Sum across all households and convert to billions
                total_cost = df[cost_col].sum() / 1e9
                cost_data[end_use_name][source_name] = total_cost
            else:
                cost_data[end_use_name][source_name] = 0
    
    # ============================================
    # FIGURE 1: Canva Diagram Placeholder
    # ============================================
    fig1 = plt.figure(figsize=(8, 6))
    ax1 = fig1.add_subplot(1, 1, 1)
    
    ax1.text(0.5, 0.5, 'PLACEHOLDER:\nEnd Use Diagram\nfrom Canva\n\n(House illustration\nshowing water heater,\nHVAC, appliances, etc.)',
             ha='center', va='center', fontsize=16, 
             bbox=dict(boxstyle='round,pad=1', facecolor=PSE_COLORS['forest_green_lighter'], 
                      edgecolor=PSE_COLORS['forest_green'], linewidth=2),
             color=PSE_COLORS['forest_green'], fontweight='bold')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.set_title('Residential End Uses', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=18, pad=20)
    
    plt.tight_layout()
    save_figure(fig1, 'energy_costs_1')
    plt.close()
    
    # ============================================
    # FIGURE 2: Stacked Bar Chart
    # ============================================
    fig2 = plt.figure(figsize=(8, 6))
    ax2 = fig2.add_subplot(1, 1, 1)
    
    # Prepare data for stacked bar chart
    end_use_names = list(end_uses.keys())
    x = np.arange(len(end_use_names))
    width = 0.6
    
    # Create stacked bars
    bottom = np.zeros(len(end_use_names))
    
    for source_name in energy_sources.keys():
        values = [cost_data[end_use][source_name] for end_use in end_use_names]
        bars = ax2.bar(x, values, width, bottom=bottom, 
                      label=source_name, color=source_colors[source_name], 
                      alpha=0.85, edgecolor='white', linewidth=1)
        
        # Add value labels for segments > $5B
        for i, (bar, val) in enumerate(zip(bars, values)):
            if val > 5:  # Only label if > $5B
                height = bar.get_height()
                label_y = bottom[i] + height/2
                ax2.text(bar.get_x() + bar.get_width()/2., label_y,
                        f'${val:.0f}B',
                        ha='center', va='center', fontsize=9, 
                        color='white', fontweight='bold')
        
        bottom += values
    
    # Add total labels on top of each bar
    for i, total in enumerate(bottom):
        ax2.text(x[i], total + 2, f'${total:.0f}B',
                ha='center', va='bottom', fontsize=11, 
                fontweight='bold', color=PSE_COLORS['forest_green'])
    
    ax2.set_xlabel('End Use', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=14)
    ax2.set_ylabel('Annual Cost (Billions $)', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=14)
    ax2.set_title('Total U.S. Residential Energy Costs by End Use (2022)', 
                 fontweight='bold', color=PSE_COLORS['forest_green'], 
                 fontsize=16, pad=20)
    ax2.set_xticks(x)
    ax2.set_xticklabels(end_use_names, rotation=45, ha='right')
    ax2.legend(title='Energy Source', frameon=True, fancybox=True, 
              shadow=True, loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_axisbelow(True)
    
    # Set y-axis to start at 0
    ax2.set_ylim(0, max(bottom) * 1.15)
    
    plt.tight_layout()
    save_figure(fig2, 'energy_costs_2')
    plt.close()
    
    print(f"  ✓ Generated 2 separate figures: energy_costs_1.svg (diagram placeholder) and energy_costs_2.svg (stacked bar chart)")


def create_budget_impact_figure():
    """
    Figure 2: Energy burden distribution
    Generates 3 separate subplot files for responsive web layout:
    - budget_impact_donut.svg: Housing cost donut chart
    - budget_impact_households.svg: Households by burden bracket
    - budget_impact_gap.svg: Affordability gap by burden bracket
    
    The website will use CSS Grid/Flexbox to arrange these responsively
    """
    usecols = ["ECB","EAG"]
    df = pd.read_parquet(filepath_nation, columns=usecols)
    # ECB is Energy Cost Burden, EAG is Energy Affordability Gap
    # Each row represents one household
    
    # Define energy burden brackets
    bins = [0, 3, 6, 9, 12, 15, 100]
    labels = ['<3%', '3-6%', '6-9%', '9-12%', '12-15%', '15+%']
    df['burden_bracket'] = pd.cut(df['ECB'], bins=bins, labels=labels, include_lowest=True)
    
    # ============================================
    # SUBPLOT 1: Donut Chart - Housing Costs
    # ============================================
    fig1, ax1 = plt.subplots(figsize=(6, 6))
    
    # Housing budget breakdown
    housing_pct = 30  # Housing is ~30% of budget
    energy_pct = 6    # Energy target is 6% of income
    other_housing_pct = housing_pct - energy_pct
    other_expenses_pct = 100 - housing_pct
    
    sizes = [energy_pct, other_housing_pct, other_expenses_pct]
    labels_donut = [f'Energy\n{energy_pct}%', f'Other Housing\n{other_housing_pct}%', 
                    f'Other Expenses\n{other_expenses_pct}%']
    colors = [PSE_COLORS['orange'], PSE_COLORS['forest_green_light'], 
              PSE_COLORS['forest_green_lighter']]
    explode = (0.1, 0.05, 0)
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels_donut, colors=colors, 
                                        autopct='%1.0f%%', explode=explode,
                                        startangle=90, pctdistance=0.85,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    # Draw circle for donut
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax1.add_artist(centre_circle)
    
    ax1.set_title('Household Budget\nBreakdown', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=14, pad=10)
    
    plt.tight_layout()
    save_figure(fig1, 'budget_impact_donut', formats=['svg', 'png'])
    plt.close()
    
    # ============================================
    # SUBPLOT 2: Households by Burden Bracket
    # ============================================
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    # Count households in each bracket (in millions)
    household_counts = df.groupby('burden_bracket', observed=True).size() / 1e6
    
    # Color bars based on threshold
    colors_bars = [PSE_COLORS['forest_green'] if label in ['<3%', '3-6%'] 
                   else PSE_COLORS['orange'] for label in household_counts.index]
    
    bars = ax2.bar(range(len(household_counts)), household_counts.values, 
                   color=colors_bars, alpha=0.85, edgecolor=PSE_COLORS['black'], linewidth=1.5)
    
    # Add 6% threshold line
    threshold_pos = 1.5  # Between 3-6% and 6-10%
    ax2.axvline(x=threshold_pos, color='red', linestyle='--', linewidth=2.5, 
                label='6% Affordability\nThreshold', alpha=0.8, zorder=0)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, household_counts.values)):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 1,
                f'{val:.1f}M', ha='center', va='bottom', 
                fontsize=10, fontweight='bold', color=PSE_COLORS['forest_green'])
    
    ax2.set_xlabel('Energy Cost Burden (% of Income)', fontweight='bold', 
                   color=PSE_COLORS['forest_green'], fontsize=12)
    ax2.set_ylabel('Number of Households (Millions)', fontweight='bold', 
                   color=PSE_COLORS['forest_green'], fontsize=12)
    ax2.set_title('Households by Energy Burden Level', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=14, pad=15)
    ax2.set_xticks(range(len(household_counts)))
    ax2.set_xticklabels(household_counts.index)
    ax2.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_axisbelow(True)
    
    plt.tight_layout()
    save_figure(fig2, 'budget_impact_households', formats=['svg', 'png'])
    plt.close()
    
    # ============================================
    # SUBPLOT 3: Affordability Gap by Bracket
    # ============================================
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    
    # Sum affordability gap in each bracket (in billions)
    gap_totals = df.groupby('burden_bracket', observed=True)['EAG'].sum() / 1e9
    
    # Only brackets above 6% contribute to gap
    colors_bars = [PSE_COLORS['gray'] if label in ['<3%', '3-6%'] 
                   else PSE_COLORS['orange'] for label in gap_totals.index]
    
    bars = ax3.bar(range(len(gap_totals)), gap_totals.values, 
                   color=colors_bars, alpha=0.85, edgecolor=PSE_COLORS['black'], linewidth=1.5)
    
    # Add threshold line
    ax3.axvline(x=threshold_pos, color='red', linestyle='--', linewidth=2.5, 
                label='6% Threshold', alpha=0.8, zorder=0)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, gap_totals.values)):
        if val > 0.5:  # Only label if > $0.5B
            ax3.text(bar.get_x() + bar.get_width()/2., val + 0.5,
                    f'${val:.1f}B', ha='center', va='bottom', 
                    fontsize=10, fontweight='bold', color=PSE_COLORS['forest_green'])
    
    ax3.set_xlabel('Energy Cost Burden (% of Income)', fontweight='bold', 
                   color=PSE_COLORS['forest_green'], fontsize=12)
    ax3.set_ylabel('Total Affordability Gap (Billions $)', fontweight='bold', 
                   color=PSE_COLORS['forest_green'], fontsize=12)
    ax3.set_title('Energy Affordability Gap by Burden Level', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=14, pad=15)
    ax3.set_xticks(range(len(gap_totals)))
    ax3.set_xticklabels(gap_totals.index)
    ax3.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    ax3.grid(True, alpha=0.3, axis='y')
    ax3.set_axisbelow(True)
    
    plt.tight_layout()
    save_figure(fig3, 'budget_impact_gap', formats=['svg', 'png'])
    plt.close()
    
    print(f"  ✓ Generated 3 separate subplot files for responsive layout")

# %%
# Load GIS data only if geopandas is available
if gpd is not None:
    try:
        gdf_nation = gpd.read_file(os.path.join("..","processed_data/tl_2022_us_tract.zip"))
    except Exception as e:
        print(f"⚠ Could not load GIS data: {e}")
        gdf_nation = None
else:
    gdf_nation = None

# %%
def adjust_gdf_50_states(gdf,state_column = "STATEFP",label_alaska = "02",label_hawaii = "15"):
    """
    Adjusts the gdf so that Alaska and Hawaii are below the US
    """
    def translate_geometries(df, x, y, scale, rotate):
        df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
        center = df.dissolve().centroid.iloc[0]
        df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
        df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)
        return df
    crs_in = gdf.crs
    gdf = gdf.to_crs("ESRI:102003").copy()
    gdf_main_land = gdf[~gdf.STATEFP.isin([label_alaska, label_hawaii])]
    gdf_alaska = gdf[gdf.STATEFP == label_alaska]
    gdf_hawaii = gdf[gdf.STATEFP == label_hawaii]

    gdf_alaska = translate_geometries(gdf_alaska, 1300000, -4900000, 0.5, 32)
    gdf_hawaii = translate_geometries(gdf_hawaii, 5400000, -1500000, 1, 24)

    gdf = pd.concat([gdf_main_land, gdf_alaska, gdf_hawaii])
    return gdf.to_crs(crs_in)


def create_ghg_emissions_figure():
    """
    Figure 3: Residential greenhouse gas emissions
    Single map: 
    - Load the first and second dots for each county 
    - Load Energy consumption data and co2e data
    - Multiply and sum electric and fossil fuel CO2e emissions for each household by county
    - Make map of the electric emission with the first dot for each county
    """
    schema = read_parquet_schema_df(filepath_nation)
    columns = schema['column'].tolist()
    usecols = ["co2e_kgs_EL", "co2e_kgs_FO", "co2e_kgs_LP", "co2e_kgs_NG","GEOID", "EL_TOTAL","NG_TOTAL","FO_TOTAL","LP_TOTAL"]
    df = pd.read_parquet(filepath_nation, columns=usecols)
    df["GEOID_COUNTY"] = np.floor(df["GEOID"]/10**6).astype(int)
    df["Electricity_CO2e"] = df["co2e_kgs_EL"] * df["EL_TOTAL"]
    df["FossilFuel_CO2e"] = (df["co2e_kgs_FO"] * df["FO_TOTAL"] +
                             df["co2e_kgs_LP"] * df["LP_TOTAL"] +
                             df["co2e_kgs_NG"] * df["NG_TOTAL"])
    df_county = df.groupby("GEOID_COUNTY").agg({
        "Electricity_CO2e": "sum",
        "FossilFuel_CO2e": "sum",}).reset_index()

    json_filepath = os.path.join("..", "affordability_data", "affordability_tool_gis_data", "national", "points_county.json")
    with open(json_filepath, "r") as f:
        points_data = json.load(f)
    
    # Extract first coordinate pair for each county
    county_coords = []
    for geoid, coords_list in points_data.items():
        if coords_list and len(coords_list) > 0:
            # First coordinate pair [lon, lat]
            first_coord = coords_list[0]
            second_coord = coords_list[1]
            county_coords.append({
                'GEOID_COUNTY': int(geoid),
                'lon_first': first_coord[0],
                'lat_first': first_coord[1],
                'lon_second': second_coord[0],
                'lat_second': second_coord[1],
            })
    
    df_points_county = pd.DataFrame(county_coords)
    
    # Merge emissions data with county coordinates
    df_map = df_points_county.merge(df_county, on="GEOID_COUNTY", how="inner")
    
    # ============================================
    # MATPLOTLIB STATIC VERSION: Single Map with Offset Dots
    # ============================================
    
    # Prepare data for both fuel types with offset coordinates
    # Electricity uses first coordinate, Fossil Fuel uses second coordinate (offset)
    electricity_mmt = df_map["Electricity_CO2e"] / 1e9  # Convert to million metric tons
    fossilfuel_mmt = df_map["FossilFuel_CO2e"] / 1e9
    
    # Create single figure
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    # Plot Electricity emissions (using first coordinate)
    scatter_elec = ax.scatter(
        df_map["lon_first"], 
        df_map["lat_first"],
        s=electricity_mmt * 5,  # Size proportional to emissions
        c=PSE_COLORS['orange'],  # Orange for electricity
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        label='Electricity'
    )
    
    # Plot Fossil Fuel emissions (using second coordinate - offset)
    scatter_fossil = ax.scatter(
        df_map["lon_second"], 
        df_map["lat_second"],
        s=fossilfuel_mmt * 5,  # Size proportional to emissions
        c=list_colors_cyans[1],  # Cyan for fossil fuels
        alpha=0.7,
        edgecolors='black',
        linewidth=0.5,
        label='Fossil Fuels'
    )
    
    # Add legend with size reference
    legend1 = ax.legend(loc='upper right', frameon=True, fancybox=True, 
                       shadow=True, fontsize=12, title='Energy Source',
                       title_fontsize=13)
    
    # Add size legend (manually create size reference)
    size_values = [1, 5, 10]  # Million metric tons
    size_labels = ['1 MMT', '5 MMT', '10 MMT']
    legend_elements = [plt.scatter([], [], s=val*5, c='gray', alpha=0.7, 
                                  edgecolors='black', linewidth=0.5, label=label)
                      for val, label in zip(size_values, size_labels)]
    legend2 = ax.legend(handles=legend_elements, loc='lower right', frameon=True, 
                       fancybox=True, shadow=True, fontsize=11, title='Emissions (MMT CO₂e)',
                       title_fontsize=12)
    ax.add_artist(legend1)  # Add both legends
    
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Turn off all axes, grid, labels - just show dots and legend
    
    plt.tight_layout()
    save_figure(fig, 'ghg_emissions_static', formats=['svg', 'png'])
    plt.close()
    
    print(f"  ✓ Generated static GHG emissions map with {len(df_map)} counties")
    
    # ============================================
    # PLOTLY INTERACTIVE VERSION: With Hover Actions
    # ============================================
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
        
        # Prepare data for Plotly
        fig_plotly = go.Figure()
        
        # Add Electricity trace
        fig_plotly.add_trace(go.Scattermap(
            lat=df_map["lat_first"],
            lon=df_map["lon_first"],
            mode='markers',
            marker=dict(
                size=electricity_mmt * 2,  # Size proportional to emissions
                color=PSE_COLORS['orange'],  # Orange for electricity
                opacity=0.7
            ),
            text=df_map["GEOID_COUNTY"].astype(str),
            customdata=np.column_stack((
                electricity_mmt,
                df_map["GEOID_COUNTY"]
            )),
            hovertemplate='<b>Electricity</b><br>' +
                         'County GEOID: %{customdata[1]}<br>' +
                         'Emissions: %{customdata[0]:.2f} MMT CO₂e<br>' +
                         'Lat: %{lat:.3f}, Lon: %{lon:.3f}<br>' +
                         '<extra></extra>',
            name='Electricity',
            showlegend=True
        ))
        
        # Add Fossil Fuel trace
        fig_plotly.add_trace(go.Scattermap(
            lat=df_map["lat_second"],
            lon=df_map["lon_second"],
            mode='markers',
            marker=dict(
                size=fossilfuel_mmt * 2,  # Size proportional to emissions
                color=list_colors_cyans[1],  # Cyan for fossil fuels
                opacity=0.7
            ),
            text=df_map["GEOID_COUNTY"].astype(str),
            customdata=np.column_stack((
                fossilfuel_mmt,
                df_map["GEOID_COUNTY"]
            )),
            hovertemplate='<b>Fossil Fuels</b><br>' +
                         'County GEOID: %{customdata[1]}<br>' +
                         'Emissions: %{customdata[0]:.2f} MMT CO₂e<br>' +
                         'Lat: %{lat:.3f}, Lon: %{lon:.3f}<br>' +
                         '<extra></extra>',
            name='Fossil Fuels',
            showlegend=True
        ))
        
        # Update layout
        fig_plotly.update_layout(
            title=dict(
                text='Residential CO₂ Emissions by County and Energy Source<br><sub>Dot size proportional to emissions (Million Metric Tons CO₂e)</sub>',
                font=dict(size=18, family="Source Sans Pro", color=PSE_COLORS['forest_green'])
            ),
            mapbox=dict(
                style='carto-positron',  # Light basemap
                center=dict(lat=39.8283, lon=-98.5795),  # Center of USA
                zoom=3
            ),
            font=dict(family="Source Sans Pro", size=14),
            hovermode='closest',
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor=PSE_COLORS['forest_green'],
                borderwidth=2
            ),
            height=700,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        # Save as HTML
        html_path = OUTPUT_DIR / 'ghg_emissions_interactive.html'
        pio.write_html(fig_plotly, html_path, include_plotlyjs='cdn')
        print(f"  ✓ Saved interactive map: {html_path}")
        
    except ImportError as e:
        print(f"  ⚠ Could not create interactive Plotly map: {e}")
    
    print(f"  ✓ Generated GHG emissions maps with {len(df_map)} counties")

def create_why_this_matters_figure():
    """
    For now, just make a placeholder figure.
    Eventually, this could be a custom infographic.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    
    ax.text(0.5, 0.5, 'PLACEHOLDER:\nInfographic\nfrom Canva\n\n(Why This Matters)',
             ha='center', va='center', fontsize=16, 
             bbox=dict(boxstyle='round,pad=1', facecolor=PSE_COLORS['forest_green_lighter'], 
                      edgecolor=PSE_COLORS['forest_green'], linewidth=2),
             color=PSE_COLORS['forest_green'], fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Why This Matters', fontweight='bold', 
                  color=PSE_COLORS['forest_green'], fontsize=18, pad=20)
    
    plt.tight_layout()
    save_figure(fig, 'why_this_matters')
    plt.close()
    
    print(f"✓ Generated placeholder figure: why_this_matters.svg")



def create_interactive_plotly_figure():
    """
    Example: Create interactive figure using Plotly
    These can be embedded in the website as HTML or JSON
    """
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
        
        # Sample data
        categories = ['Space Heating', 'Water Heating', 'Cooling', 'Appliances', 'Other']
        
        fig = go.Figure()
        
        # Add traces for different income groups
        fig.add_trace(go.Bar(
            name='Low-Income',
            x=categories,
            y=[850, 320, 180, 420, 230],
            marker_color=PSE_COLORS['orange']
        ))
        
        fig.add_trace(go.Bar(
            name='All Households',
            x=categories,
            y=[720, 280, 220, 380, 200],
            marker_color=PSE_COLORS['forest_green']
        ))
        
        fig.update_layout(
            title='Annual Energy Costs by End Use',
            xaxis_title='End Use',
            yaxis_title='Average Annual Cost ($)',
            barmode='group',
            font=dict(family="Source Sans Pro", size=14),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='x unified'
        )
        
        # Save as HTML (can be embedded via iframe)
        html_path = OUTPUT_DIR / 'interactive_costs.html'
        pio.write_html(fig, html_path, include_plotlyjs='cdn')
        print(f"✓ Saved {html_path} (Interactive HTML)")
        
        # Save as JSON (for custom integration)
        json_path = OUTPUT_DIR / 'interactive_costs.json'
        fig.write_json(json_path)
        print(f"✓ Saved {json_path} (Plotly JSON)")
        
    except ImportError:
        print("⚠ Plotly not installed. Install with: pip install plotly")


def generate_all_figures():
    """
    Generate all website figures
    """
    print("=" * 60)
    print("Generating figures for Affordability Website")
    print("=" * 60)
    print()
    
    # print("1. Creating Energy Costs figure...")
    # create_energy_costs_figure()
    # print()
    
    # print("2. Creating Budget Impact figure...")
    # create_budget_impact_figure()
    # print()
    
    print("3. Creating GHG Emissions figure...")
    create_ghg_emissions_figure()
    print()
    
    print("4. Creating Why This Matters figure...")
    create_why_this_matters_figure()
    print()
    
    # print("5. Creating Interactive Plotly figure...")
    # create_interactive_plotly_figure()
    # print()
    
    print("=" * 60)
    print("✓ All figures generated successfully!")
    print(f"✓ Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    print()
    print("USAGE IN HTML:")
    print("  <!-- SVG (recommended) -->")
    print("  <img src='assets/energy_costs.svg' alt='Energy Costs'>")
    print()
    print("  <!-- WebP with PNG fallback -->")
    print("  <picture>")
    print("    <source srcset='assets/energy_costs.webp' type='image/webp'>")
    print("    <img src='assets/energy_costs.png' alt='Energy Costs'>")
    print("  </picture>")
    print()
    print("  <!-- Interactive Plotly -->")
    print("  <iframe src='assets/interactive_costs.html' ")
    print("          width='100%' height='600px' frameborder='0'></iframe>")


if __name__ == "__main__":
    generate_all_figures()

# %%