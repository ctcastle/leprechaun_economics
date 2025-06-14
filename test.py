import pandas as pd 
import numpy as np 

def convert(val):
    val = str(val)
    if "k" in val:
        val = val.replace("k","")
        val = float(val)*1_000
    elif "M" in val:
        val = val.replace("M","")
        val = float(val)*1_000_000
    elif "B" in val:
        val = val.replace("B","")
        val = float(val)*1_000_000_000
    elif "TR" in val:
        val = val.replace("TR","")
        val = float(val)*1e12
    else:
        float(val)
    return val

# Import data 
gdp_percap = pd.read_csv("gdppercapita_us_inflation_adjusted.csv")
total_gdp = pd.read_csv("total_gdp_us_inflation_adjusted.csv")
gini = pd.read_csv("gini.csv")

# Set index to country 
gdp_percap = gdp_percap.set_index('country')
total_gdp = total_gdp.set_index('country')
gini = gini.set_index('country')

# Convert any string to a number - data prep - DONE 
gdp_percap_copy = gdp_percap.map(lambda x:convert(x),na_action = 'ignore')
total_gdp_copy = total_gdp.map(lambda x:convert(x),na_action = 'ignore')


# Merge the data together into hierarchical index - concat - DONE 
# Only outer to ensure data shares values 
combined_data = pd.concat([total_gdp_copy, gdp_percap_copy, gini], axis=0,join='inner', keys=['Total GDP', 'GDP Per Capita', 'Gini Coeff'])
combined_data.index.names = ['Metric', 'Country']
print(combined_data.size)

# Check for any country with more than X NANs 
# Drop or handle 
# Plot every country per year?? 
# Plot continent blocks?? 
# Look for any outliers 
# Explain those 
# Plot average, median, etc. global GDP per year?? 
