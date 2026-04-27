# National Energy Affordability Tool Guide

A comprehensive guide to using the interactive dashboard for energy equity analysis. The tool has two main sections: the **Existing Affordability Landscape Tool** for exploring current conditions, and the **Decision Support Tool** for modeling policy interventions.

---

## Existing Affordability Landscape Tool

The Existing Affordability Landscape Tool allows you to explore comprehensive data on energy costs, consumption, emissions, and affordability gaps across the United States. This section describes each component of the interface.


### Geographies

The Geography selector determines the spatial unit of analysis for all visualizations and statistics.

**Available geography types:**

- **Nationwide:** Aggregate statistics for the entire United States
- **States:** All 50 states plus Washington D.C.
- **Counties:** Over 3,000 U.S. counties
- **Utility Service Territories:** Electric utility boundaries
- **Metropolitan Areas:** Census-defined metro/micro statistical areas

**How to use:**

1. Select the geography type from the dropdown menu
2. For counties and utilities, you can further filter by state
3. Use the search box to find specific geographies by name
4. Selected geographies will be highlighted on the map

### Filtering Households

The filtering panel allows you to narrow your analysis to specific household types based on demographic and housing characteristics.

**Available filters:**

- **Income Level:** 
  - By Area Median Income (AMI) brackets (0-30%, 30-60%, 60-80%, 80-100%, >100%)
  - By Federal Poverty Level (FPL)
  - By absolute income ranges

- **Housing Characteristics:**
  - Building type (single-family detached, single-family attached, multifamily 2-4 units, multifamily 5+ units, mobile home)
  - Tenure (owner-occupied, renter-occupied)
  - Year built (vintage categories)

- **Heating Fuel:**
  - Electricity
  - Natural gas
  - Propane/LPG
  - Fuel oil
  - Other fuels

- **Demographics:**
  - Race/ethnicity of householder
  - Age of householder
  - Household size

**Tips for filtering:**
- Multiple selections within a category are combined with OR logic
- Selections across categories are combined with AND logic
- The household count updates in real-time as you apply filters

### Affordability Map

The interactive map displays spatial patterns in energy affordability metrics across your selected geography.

**Map features:**

- **Choropleth coloring:** Geographic units are shaded based on the selected metric
- **Color scale:** Adjustable color ramps with automatic or custom break points
- **Hover information:** Mouse over any region to see detailed statistics
- **Click to select:** Click a region to focus the analysis on that geography
- **Zoom and pan:** Navigate using mouse scroll and drag

**Available metrics for mapping:**

- Energy burden (% of income spent on energy)
- Energy costs (annual $ spent)
- Affordability gap ($ above 6% threshold)
- Energy consumption (kWh, therms)
- Greenhouse gas emissions (CO₂e)
- Household counts

### Summary Statistics

The Summary Statistics panel provides aggregate numerical summaries for your current selection.

**Statistics displayed:**

- **Household counts:** Total households and filtered subset
- **Energy costs:** Mean, median, total annual costs
- **Energy burden:** Mean and median burden rates, distribution
- **Affordability gap:** Total gap, households exceeding threshold
- **Consumption:** Average electricity (kWh) and gas (therms)
- **Emissions:** Total and per-household CO₂ equivalent

**Export options:**
- Download statistics as CSV
- Copy to clipboard
- Generate formatted report

### Bar Chart

The Bar Chart visualization allows comparison of metrics across categories or geographies.

**Chart options:**

- **X-axis:** Choose categorical variable (geography, income group, housing type, etc.)
- **Y-axis:** Select metric to display (costs, burden, consumption, emissions)
- **Aggregation:** Sum, mean, median, or count
- **Sorting:** Ascending, descending, or alphabetical
- **Grouping:** Stack or group bars by a second category

**Interactivity:**
- Hover for exact values
- Click bars to filter data
- Drag to reorder categories
- Export as PNG or SVG

### Scatter Chart

The Scatter Chart shows relationships between two continuous variables across geographic units.

**Configuration:**

- **X-axis variable:** Any numeric metric
- **Y-axis variable:** Any numeric metric
- **Point size:** Optionally scale by household count or other metric
- **Point color:** Optionally color by categorical variable

**Common use cases:**
- Income vs. energy burden relationship
- Consumption vs. emissions correlation
- Geographic comparison of multiple metrics

**Interactivity:**
- Hover to identify geographic units
- Lasso select to filter
- Zoom to region of interest

### Network Graph

The Network Graph visualizes relationships and flows between entities in the energy system.

**Applications:**

- Utility service territory relationships
- Energy flow patterns
- Program coverage networks

**Features:**
- Interactive node positioning
- Edge weight visualization
- Community detection
- Filter by connection strength

### Treemap

The Treemap displays hierarchical data as nested rectangles, useful for understanding composition and proportions.

**Use cases:**

- Share of energy costs by fuel type
- Household distribution by income bracket
- Geographic contribution to total emissions

**Features:**
- Hierarchical drill-down
- Size by any numeric metric
- Color by category or value
- Interactive labels

---

## Decision Support Tool

The Decision Support Tool allows you to model the impacts of energy efficiency programs, weatherization initiatives, electrification policies, and rate changes on household energy costs and emissions.



### Inputs

The Input panel is where you configure the policy scenario to model. Parameters are organized into accordion sections for easy navigation.

**Accessing the inputs:**
1. Click "Open Policy Scenario" or the settings icon
2. A modal window opens with collapsible accordion sections
3. Configure parameters in each relevant section
4. Click "Run Scenario" to execute the model

> **Note:** The geography and population scope is determined by your selections in the main Existing Affordability Landscape Tool. Use the filters there to target specific regions and household types before opening the Policy Scenario modal.

#### Accordion Categories

Each accordion section contains related parameters for different types of interventions. The sections are organized into two columns:

---

##### Left Column

**� Rate Changes (Energy Prices)**

View current average rates and enter new rates to model price changes. Leave blank to keep current rate.

- **Electricity Rate** (¢/kWh): Current rate shown; enter new rate to model changes
- **Natural Gas Rate** ($/therm): Current rate shown; enter new rate to model changes
- **Propane Rate** ($/gal): Current rate shown; enter new rate to model changes
- **Fuel Oil Rate** ($/gal): Current rate shown; enter new rate to model changes

**🌱 Grid Decarbonization (CO₂e)**

Adjust the carbon intensity of electricity. This affects household emissions calculations.

- **Electricity Carbon Intensity** (kg CO₂e/kWh): Enter the emissions factor for your grid scenario
- Typical values: 0.2-0.4 for cleaner grids, 0.5-0.8 for coal-heavy grids
- Lower values = cleaner electricity

**🏠 Energy Efficiency Improvements**

Apply efficiency improvements to reduce energy consumption. Choose your preferred grouping mode:

- **By End Use** (4 sliders): All Space Heating, All Space Cooling, All Water Heating, All Appliances & Other
- **By Fuel Type** (4 sliders): Group savings by electricity, natural gas, propane, fuel oil
- **Detailed - By End Use & Fuel** (15 sliders): Granular control over each fuel/end-use combination

Each slider reduces BTU consumption by the specified percentage for participating households.

**Efficiency Program Participants:** Use the adoption selector to specify participation rates—either percentage of households or total household count.

---

##### Right Column

**⚡ Fuel Switching (Electrification)**

Configure fuel switching scenarios—switch from fossil fuels to electricity.

- **Add Fuel Switch:** Click to add a new fuel switch row
- For each switch, specify:
  - Source fuel (natural gas, propane, fuel oil)
  - End use (space heating, water heating, other)
  - Target fuel (electricity)
  - Adoption rate or household count

**Heat Pump Efficiency (SCOP):** Applies to all fuel switches to electric heating/cooling
- **Space Heating Heat Pump SCOP:** Seasonal Coefficient of Performance (typical range 2.5-4.5)
- **Water Heating Heat Pump SCOP:** Seasonal Coefficient of Performance (typical range 2.0-3.5)
- Higher SCOP values = more efficient heat pumps

**🔄 Heat Pump Replacement (Electric Systems)**

Replace existing electric heating/water systems with more efficient heat pumps (electric → electric upgrade).

- Specify replacement rates for existing electric resistance systems
- Set efficiency improvements for upgraded systems
- ⚠️ Backend support pending—parameters will be saved but not yet processed

**📊 Demand Response Programs**

Incentives for households participating in demand response programs (load shifting, peak reduction).

- **All-Electric Households Discount** ($/yr): Annual discount for all-electric participants
- **Hybrid Fuel Households Discount** ($/yr): Annual discount for hybrid fuel participants
- For each discount, specify adoption rate (percentage or count)
- All-electric homes typically receive higher incentives

**💰 Bill Assistance Programs**

Low-income energy assistance with optional income targeting (FPL or AMI).

**Program Type:**
- **Bill Discounts:** Fixed monthly discounts or percentage discounts
  - Electric Bill Discount ($/mo)
  - Gas Bill Discount ($/mo)
  - Electric Bill Percentage Discount (%)
  - Gas Bill Percentage Discount (%)
- **PIPP Program:** Percentage of Income Payment Plan
  - Energy burden cap (% of income)
  - Income eligibility thresholds

**Income Targeting:** Optionally limit eligibility by FPL or AMI threshold.

**☀️ Solar Programs**

Rooftop or community solar benefits. Choose between simple percentage offset or advanced generation distribution.

**Solar Method:**
- **Percentage Offset:** Simple rooftop solar
  - Solar Offset Percentage (% offset)
  - Example: 30% = rooftop solar covering 30% of usage
- **Generation Distribution:** Community solar
  - Total Solar Generation (MWh/year)
  - Value per kWh ($)
  - Distributes fixed solar generation proportionally among participants based on electricity usage

**🔋 Energy Storage (Battery)**

Battery storage savings from time-of-use load shifting (charging off-peak, discharging on-peak).

- **Daily Load Shift per Household** (kWh): Amount of load shifted daily
- **TOU Price Differential** ($/kWh): Price difference between peak and off-peak
- Specify adoption rate for participating households

### Results

After running a scenario, the Results panel displays the projected impacts of your intervention.

#### Map

The Results Map shows the spatial distribution of policy impacts across your selected geography.

**Map displays:**

- **Baseline vs. Scenario comparison:** Toggle between current conditions and modeled outcomes
- **Change metrics:** Absolute or percentage change in key indicators
- **Benefit distribution:** Where impacts are concentrated

**Key metrics mapped:**
- Change in average energy burden
- Reduction in affordability gap
- Energy cost savings
- Emission reductions
- Households benefiting

**Interactivity:**
- Side-by-side comparison view
- Animation showing transition
- Click for detailed regional breakdown

#### Graph

The Results Graph provides quantitative summaries and comparisons of scenario outcomes.

**Visualization types:**

- **Before/After bar charts:** Compare baseline to scenario for selected metrics
- **Distribution curves:** Show how burden distribution shifts
- **Cost-benefit analysis:** Total program costs vs. household savings
- **Emissions waterfall:** Sources of emission reductions

**Key outputs:**

- Total annual savings ($ millions)
- Average household savings ($)
- Households achieving affordability (%)
- Emission reductions (tons CO₂e)
- Program cost estimates
- Cost-effectiveness metrics ($/ton CO₂e, $/household)

**Export options:**
- Download results summary (CSV, Excel)
- Export visualizations (PNG, SVG)
- Generate scenario report (PDF)

---

## Tips & Best Practices

### Getting Started

1. **Start with exploration:** Use the Existing Affordability Landscape Tool to understand baseline conditions
2. **Identify priorities:** Look for areas with high burden rates or large affordability gaps
3. **Design interventions:** Use the Decision Support Tool to model targeted policies
4. **Compare scenarios:** Run multiple scenarios to evaluate trade-offs

### For Researchers

- Always note the data year (2022) when citing statistics
- Document filter settings used in your analysis
- Use the export feature for reproducible workflows
- Cross-reference with local data sources when available

### For Policymakers

- Start with state or utility-level views for jurisdiction-specific insights
- Compare burden rates across demographic groups to identify equity concerns
- Use affordability gap estimates for program sizing and budget planning
- Model multiple intervention types to find optimal policy mix

### For Advocates

- Generate community-specific statistics for local advocacy
- Visualize disparities with demographic breakdowns
- Download charts and maps for presentations and reports
- Track how proposed policies would benefit target communities

---

## Frequently Asked Questions

### What year does the data represent?

The current version uses 2022 data. We plan to update annually as new source data becomes available.

### How accurate are the estimates?

Estimates are based on statistical modeling and carry inherent uncertainty. See the [Methodology](methodology.html) page for details on our approach and validation.

### Can I download the underlying data?

Yes, the Statistics Generator includes export functionality for all visualizations and summary statistics. Household-level microdata is not available for download.

### How do I cite this tool?

Citation guidance will be provided with our methodology publication. In the meantime, please reference: "National Energy Affordability Tool, PSE Healthy Energy, 2024."

### Who do I contact for help?

For technical questions or to report issues, please contact PSE Healthy Energy through our [website](https://www.psehealthyenergy.org/contact/).
