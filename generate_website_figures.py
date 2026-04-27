# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
from matplotlib.patches import ConnectionPatch
dict_colors_pse = {
    "Light Blue":"#C4F2EB",
    "Sea Green":"#6BD6CC",
    "Black":"#252728",
    "Orange":"#F7911E",
    "Forest Green":"#275258",
    "Cool Gray":"#C4C2C4"
}

def normalize_colors(color_list):
    return [(r/255, g/255, b/255) for r, g, b in color_list]

list_colors_blacks = normalize_colors([(37,39,40),(110,110,110),(150,150,150),(196,195,198)])
list_colors_blues = normalize_colors([(33,76,111),(57,116,147),(123,171,190),(169,204,217)])
list_colors_reds = normalize_colors([(196,38,45),(240,76,59),(244,124,93),(249,172,141)])
list_colors_oranges = normalize_colors([(247,104,40),(247,135,30),(247,173,75),(255,206,107)])
list_colors_cyans = normalize_colors([(39,82,88),(0,167,158),(107,214,204),(196,242,235)])


# %%
"""
# Greenhouse Gases from Homes
Occupied homes are responsible for XX tons of greenhouse gases which represent XX% of direct emissions in the US. Low-income households alone are responsible for XX and XX% respectively.

# Why this Matters
Households that struggle to pay their bills face increased risks to health and safety. Moreover, they struggle to afford the upfront costs to solutions that can reduce their bills and/or emissions. Programs such as XX and XX help, but they benefit from data informed by local data around climate, home type, and demographics such as renter status.

# Our Tool
For this reason, we developed the first tool to aggregate costs, emissions, and more that relies on a simulated data set of all households in 2022.  

"""

# %%
"""
# Costs for Energy at Home
Households paid roughly \$XX billion in 2022 for electricity and fossil fuels to run their homes. Low-income households with earning less than 80\% of the area median income were responsible for \$XX billion or XX\%.

To accompany above text, make the following figure.
Left, a pie chart of all the total spending for electricity,
propane, gas, and fuel oil. Label each piece of the pie with 
the dollar amount and also add a title that labels the total value.

Right, a stacked bar chart of the total spending by 0-80% of AMI
, 80-15% of AMI, and >150% AMI. 

"""
# First, let's generate some pretend data for now.
cost_by_fuel_type = {"Electricity": 100, "Propane": 50, "Gas": 200, "Fuel Oil": 50}
cost_by_AMI_bracket_end_use = {"0-80%":{ "Space\n Heating": 50, "Space\n Cooling": 25, "Water\n Heating": 100, "Other": 25},
                                "80-150%":{ "Space\n Heating": 50, "Space\n Cooling": 25, "Water\n Heating": 100, "Other": 25},
                                ">150%":{ "Space\n Heating": 50, "Space\n Cooling": 25, "Water\n Heating": 100, "Other": 25}}

# Font for axes should be Source Sans Pro Regular, and labels should be Source Sans Pro Bold
# Colors should be the ones from the dict_colors_pse
# Donut chart
fig, axs = plt.subplots(1,2, figsize=(8,4))
# Ensure source sans pro is installed
plt.rcParams['font.family'] = 'Source Sans Pro'
plt.rcParams['font.weight'] = 'regular'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 14

# Use a donut chart
my_circle = plt.Circle( (0,0), 0.7, color=dict_colors_pse["Cool Gray"])
# Add text to the center of the donut chart
total_spending = sum(cost_by_fuel_type.values())
axs[0].text(0, 0, "$"+str(total_spending)+"\nBillion", ha='center', va='center', fontsize=20, color=dict_colors_pse["Black"])

# Give color names
slice_colors = list_colors_blues
# Make custom labels that inclue the dollar amount and a new line character
labels = [f"{key}\n${value}" for key, value in cost_by_fuel_type.items()]
p = axs[0].pie(cost_by_fuel_type.values(), labels=labels, colors=slice_colors)
axs[0].add_artist(my_circle)
axs[0].set_title(f"Total Spending on Energy")

# Set the background color of the whole chart to light grey
fig.patch.set_facecolor(dict_colors_pse["Cool Gray"])

# Now make the right figure stacked bar chart.
# Make the data into a dataframe
df = pd.DataFrame(cost_by_AMI_bracket_end_use)
df = df.T
df = df[["Space\n Heating", "Space\n Cooling", "Water\n Heating", "Other"]]
# Make the stacked bar chart
bar_colors = list_colors_cyans
df.plot(kind='bar', stacked=True, ax=axs[1], color=bar_colors)
axs[1].set_title("Total Spending by Income Bracket")
axs[1].set_ylabel("Total Spending in Billion $")
axs[1].set_xlabel("Household Area Median Income")
# Make space for the legend
# Move the legend to the top of the plot with two columns
axs[1].legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=2, frameon=True)
# Set the background color of the legend to light grey
legend = axs[1].legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=2, frameon=True)
legend.get_frame().set_facecolor(dict_colors_pse["Cool Gray"])
# Set the background color of axs[1] to light grey
axs[1].patch.set_facecolor(dict_colors_pse["Cool Gray"])
# Adjust the y-axis limits to make space for the legend
y_max = axs[1].get_ylim()[1]
axs[1].set_ylim(0, y_max * 1.6)
# despine axs[1]
sns.despine(ax=axs[1])

# Set the x-axis label rotation to 0
plt.xticks(rotation=0)
plt.tight_layout()
# Set the background color of the legend to light grey
# Show the graph
plt.show() 

# Export to a good format for uploading to a webpage
fig.savefig(os.path.join("assets","energy_costs.png"), dpi=300, bbox_inches='tight', transparent=True)

# %%
"""
# Energy Bills as Portions of Income
For low-income households, XX\% of households spent more than 6% of their gross income on energy. 
Taking just the portions of energy costs that exceed 6% of gross income, we estimate a sum of $XX billion needed annualy in bill assistance to ensure households do not spend more than 6% of their income on energy at home.

For this part, I want some basic stats
On the left, some text of how many millions of households spend more than 6%
Then, below that, a stat of how many are energy insecure

Then, on the right, a visual of 
"""
"""
Brainstorming:
- A pie chart of the percentage of households that spend more than 6% of their income on energy
- A 
"""


# %%

# %%

# %%

