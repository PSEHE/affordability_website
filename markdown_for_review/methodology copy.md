# Methodology & Data

How we estimate energy costs, consumption, and burden for every household in the United States.

## Overview

The National Energy Affordability Tool (NEAT) estimates household-level energy costs, consumption, and emissions for all occupied housing units in the United States. Direct measurements don't exist at this scale, so we built a *synthetic household dataset* —a statistically representative set of simulated households for every census tract, each with realistic demographic and housing characteristics, energy usage, and costs.

This synthetic household dataset weaves together several large national datasets including household surveys, utility records, and census data. The result is a census tract-level dataset covering all ~84,000 tracts in the U.S. that is suitable for identifying energy burden hotspots, demographic disparities, and policy intervention opportunities.

## Data Sources

The data underlying the tool integrates six major national datasets. Each plays a distinct role in the modeling pipeline to develop the synthetic household dataset.

#### American Community Survey

ACS 5-Year · U.S. Census Bureau

Tract-level counts of households by income bracket, housing type, housing tenure, heating fuel, year built, household size, and race/ethnicity. These serve as the hard constraints for household allocation.

#### Public Use Microdata Sample

PUMS · U.S. Census Bureau

Anonymized individual household records with detailed demographics, housing characteristics, income, and housing costs. The source pool from which households are allocated to tracts.

#### Residential Energy Consumption Survey

RECS 2020 · U.S. EIA

Nationally representative survey of ~18,500 U.S. households with detailed end-use energy consumption. Used to train all energy prediction models.

#### American Housing Survey

AHS · U.S. Census Bureau

Detailed housing unit characteristics including floor area, AC type, and utility payment status. Used to train housing characteristics models, with metro-level samples for 35 major metros.

#### EIA Form 861 & SEDS

U.S. Energy Information Administration

Utility service territory boundaries and electricity retail rates (Form 861), plus state-level residential fuel prices by type (State Energy Data System). Used to translate energy consumption to costs.

#### eGRID & NOAA

EPA · NOAA

EPA's eGRID subregional electricity emission factors for CO₂ intensity calculations. NOAA heating and cooling degree days as climate inputs to energy models.

## Modeling Pipeline

The modeling pipeline moves data from census tract or larger geographies down to individual household estimates in five steps. Each step feeds into the next: the appropriate number of households for each census tract are allocated demographic and housing characteristics, then estimated energy consumption, then costs, then emissions.

#### Household Allocation

Each census tract in the U.S. has known demographic and housing characteristics from the **American Community Survey (ACS)**. This includes information like how many households are renters versus owners, income distributions, the share of multi-family homes, and predominant heating fuels. But the ACS reports each of these characteristics only as aggregate counts.

To get individual households, we draw from the **Public Use Microdata Sample (PUMS)**, which contains detailed records for real (anonymized) households. Using integer programming optimization, we select a combination of PUMS households for each tract whose collective profile matches the ACS counts across 70 demographic and structural variables simultaneously, including income brackets, housing type, heating fuel, year built, household size, and more.

The optimization minimizes geographic distance between the source PUMS geography and the target tract, so allocated households are drawn from nearby areas with similar regional characteristics. This integer programming approach enforces multi-way constraints (for example, **[YUNUS ADD]**) and produces whole households, allowing for accurate energy modeling.

#### Housing Characteristics Estimation

The allocated PUMS households carry many characteristics directly, but a few attributes critical for energy modeling—primarily floor area and air conditioning type—are not included in the PUMS data. So we estimated these using machine learning models trained on the **American Housing Survey (AHS)** data.

To determine floor area, we used a Gradient Boosting algorithm with housing structure (number of rooms, building type, year built, and tenure), household demographics, and geographic division as predictors. A similar approach is used to determine AC type—whether a household has central air, a window unit, or no AC. Since AC patterns vary dramatically by region, metro-specific models were used in 35 metro areas where local AHS data was available.

#### Energy Consumption Estimation

Energy use is predicted separately for 14 end-use categories—space heating by fuel (electricity, natural gas, propane, fuel oil, wood), space cooling, water heating, electric appliances, cooking, clothes drying, and fan/pump loads. Models were trained on the **Residential Energy Consumption Survey (RECS) 2020** data, which provides measured end-use energy information for roughly 18,500 U.S. households.

The appropriate model type is chosen for each end-use based on the statistical properties of that energy stream—whether consumption is near-universal or zero-inflated and how skewed the distribution is. We used a Gradient Boosting regression for most end-uses, though used a linear regression for water heating and cooking, a log-linear regression for electric appliances, and Random Forest regression for heat pump heating. (See 'Model Selection' below for more on this.)

Climate inputs (heating and cooling degree days from **NOAA**) are included to capture geographic variation in demand. End-use predictions are summed to total household energy consumption by fuel type.

#### Cost & Burden Calculation

Predicted energy consumption (in BTU or kWh) is converted to annual energy costs using local utility rates and regional fuel prices. Electricity rates come from **EIA Form 861**, which maps utilities to their service territories, allowing us to apply the correct rate for each household's location. Natural gas, propane, fuel oil, and wood prices are drawn from the **U.S. State Energy Data System (SEDS)**.

Energy burden—the share of a household's income spent on energy—is calculated by dividing a household's annual energy cost by its annual income from the PUMS data. Households spending more than 6 percent of their income on energy are commonly considered energy-burdened; those above 10% are considered highly burdened.

For the roughly 2–4 percent of households where utilities are included in rent, payment status flags from the PUMS record are included in the synthetic population dataset so these households can be distinguished during analysis.

#### Emissions Estimation

Greenhouse gas emissions are estimated for each household's energy consumption. Electricity emissions use subregional emission factors from EPA's **eGRID** database, which captures variation in grid carbon intensity across the country. On-site fuel combustion of gas, propane, oil, and/or wood uses standard combustion emission factors.

Emission estimates are provided in CO₂-equivalent, allowing comparison across fuels and informing analysis of how fuel-switching or efficiency improvements would affect both costs and emissions.

## Model Selection & Variables

Rather than using a single model type for all energy end-uses, we assign each end-use to a model family based on the statistical properties of that energy stream. This approach avoids empirical cherry-picking while still allowing the most appropriate method for each case.

### Energy consumption models

Four model types were evaluated through 10-fold cross-validation on the RECS 2020 data: Gradient Boosting regression, Random Forest regression, linear regression, and log-linear regression. Performance was compared using a cost-weighted error metric that translates BTU prediction errors into dollar errors—which weights electricity errors more heavily than gas errors, reflecting electricity's higher price per BTU.

| End-use type | Example end-uses | Model used | Reason |
| --- | --- | --- | --- |
| High-prevalence continuous | Space cooling, space heating (electric) | Gradient Boosting | Best performance on high-priority end-uses; handles non-linearity well |
| High-prevalence, small sample | Heat pump heating | Random Forest | Bagging reduces variance when fewer training examples are available |
| Moderate right-skewed | Appliances (electric), cooking | Linear or Log-linear | Simpler models outperform on moderately skewed distributions |
| Zero-inflated (few users) | Gas appliances, propane, fuel oil | Linear | Tree models overfit the zero mass; linear model most calibrated |

Across all end-uses, Gradient Boosting reduces the cost-weighted prediction error by roughly $14 per household per year compared to using Random Forest.

### Predictor variables

All end-use models share a common base feature set. End-use models for water heating, cooking, drying, and appliances additionally include the relevant fuel type for that end-use (e.g., gas vs. electric water heater) as a predictor.

| Predictor variable | Variable options |
| --- | --- |
| Building type | Single-family detached/attached, apartment (2–4 units, 5+ units), mobile home |
| Climate | Heating degree days (HDD65) and cooling degree days (CDD65) from NOAA at the household's location |
| Floor area | Estimated total conditioned square footage (from Step 2) |
| Household size | Number of occupants |
| Heating fuel type | Natural gas, electricity, propane, fuel oil, wood, or other |
| AC type | Central air, room unit, evaporative cooler, or none (from Step 2) |
| Heat pump indicator | Whether the primary heating system is a heat pump |
| All-electric indicator | Whether electricity is the sole energy source |
| Urban/rural classification | Urban or rural based on **[YUNUS ADD]** |
| Building America climate zone | Eight zones encoding regional building stock and climate norms |
| State fixed effects | FIPS-level indicators capturing state-specific program, code, and rate differences |
| Poverty ratio (FPL ratio) | Household income divided by the federal poverty level for that household size; captures income-dependent consumption behaviors (appliance ownership, thermostat settings) in a form that is independent of household size already in the model (see below) |

**Electric appliance end-use coverage:** The electric appliances end-use aggregates 14 RECS measured components: refrigerators, freezers, televisions and electronics, lighting, microwaves, clothes washers, dishwashers, dehumidifiers, humidifiers, pool pumps, hot tub pumps and heaters, ceiling fans, and miscellaneous plug loads. This is the end-use most sensitive to income, because appliance ownership rates increase substantially with household income.

### How income enters the model

Income affects energy consumption through two channels: an indirect channel (lower-income households tend to live in smaller, older homes, which is already captured by building characteristics) and a direct behavioral channel (appliance ownership, hot water use intensity, and thermostat settings all vary by income even within the same building type). Including income explicitly captures this second channel.

We use the poverty ratio (FPL ratio)—household income divided by the federal poverty level for that household size—rather than raw income. This size-adjusted measure is independent of household size, which is already in the model, avoiding the collinearity that raw income introduces. Cross-validation on RECS 2020 confirms the poverty ratio has measurable Gini importance in every end-use model.

The effect is largest for electric appliances: without the poverty ratio, predicted electricity consumption is nearly flat across income quintiles (Q5/Q1 ratio of 1.48×). With it, the model reproduces the observed RECS gradient (1.87× predicted vs. 1.89× actual). This reflects the strong income gradient in appliance ownership, wherein dishwashers, pool pumps, and numerous electronics are far more common in higher-income homes.

**What we do not include:** Raw income (collinear with household size), number-of-rooms dummies (collinear with floor area; their presence inflated income's variance inflation factor from ~1.3 to ~14, masking income's true predictive signal), and tenure (owner vs. renter; captured by building type and income).

## How the Decision Support Tool Works

The NEAT synthetic household dataset represents individual households at the census tract level. This is critical for identifying policy intervention opportunities based on energy cost burden and demographic disparities, but is too granular for direct use in an interactive web tool. To account for this, the tool works with a pre-processed, aggregated version of this data. The decision support tool adds a scenario modeling layer that lets users explore how policy changes might affect energy costs and burdens for different types of households. The underlying dataset represents individual households at the census tract level. This is critical for identifying policy intervention opportunities based on energy cost burden and demographic disparities, but is too granular for direct use in an interactive web tool. To account for this, the decision support tool works with a pre-processed, aggregated version of this data, adding a scenario modeling layer that lets users explore how policy changes might affect energy costs and burdens.

### Data aggregation for the tool

For the tool, households within specified geographic scopes from the synthetic dataset are grouped by shared characteristics and their energy and fuel usage and costs, energy burdens and affordability gaps, and emissions are aggregated. This allows us to pre-calculate statistics—such as the total energy affordability gap, mean energy burden, total energy cost, and total energy consumption—for census tracts, counties, metro areas, and utility service territories while preserving a user’s ability to see these statistics disaggregated by specific household characteristics.

For example… **[YUNUS ADD]**

Grouping households by shared characteristics also allows us to model different scenarios such as changes in energy efficiency or fuel switching from gas to electric and see how this might change household energy usage and costs across household categories.

### Scenario modeling

The decision support tool allows users to apply certain energy policy interventions to households within a specified geographic area and see how they may impact energy usage, costs, burdens, affordability gaps, and emissions for different types of households. Interventions include rate changes (e.g., changes in energy prices), fuel switching, efficiency improvements, solar programs, energy storage, and more.

Just as home energy programs follow a specific order of operations—for example, energy efficiency improvements may be required before a home electrifies and installs solar panels—the scenario modeling in the tool applies interventions in a specific sequence to understand their cumulative impact on household energy usage, costs, and emissions. For example, if a user applies both an energy efficiency improvement and a fuel switching intervention, the tool first applies the efficiency improvement before modeling the fuel switch, since the efficiency improvement would reduce householdenergy demand and thus affect the impact of the fuel switch.
