import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os 

# Data cleaning and merging

def parse_gdp_values(df):
    """ Parses monetary values in a pandas dataframe, converting string values with suffixes to floats with corresponding zeros.
        This function modifies the original dataframe.

    Args:
        df (_type_): _description_
    """
    for country in df.index:
        for year in df:
            val = df.loc[country,year]
            if isinstance(val, float):
                continue    
            val = val.strip().upper()
            if val.endswith('K'):
                df.loc[country,year] = float(val[:-1]) * 1e3
            elif val.endswith('M'):
                df.loc[country,year] = float(val[:-1]) * 1e6
            elif val.endswith('B'):
                df.loc[country,year] = float(val[:-1]) * 1e9
            elif val.endswith('TR'):
                df.loc[country,year] = float(val[:-2]) * 1e12
            else:
                df.loc[country,year] = float(val[:-1])


def df_index_inner_join(df1, df2, df3, key1, key2, key3):
    """ combines 3 pandas dataframes with an inner join along the rows

    Args:
        df1 (_type_): _description_
        df2 (_type_): _description_
        df3 (_type_): _description_
        key1 (_type_): _description_
        key2 (_type_): _description_
        key3 (_type_): _description_

    Returns:
        _type_: _description_
    """
    mask_df1 = df1.index.isin(df2.index) & df1.index.isin(df3.index)
    mask_df2 = df2.index.isin(df1.index) & df2.index.isin(df3.index)
    mask_df3 = df3.index.isin(df2.index) & df3.index.isin(df1.index)

    df1_filtered = df1[mask_df1]
    df2_filtered = df2[mask_df2]
    df3_filtered = df3[mask_df3]

    combined_data = pd.concat([df1_filtered, df2_filtered, df3_filtered], axis=0, keys=[key1, key2, key3], join='inner')
    return combined_data

def drop_countries_by_nan(df, threshold):
    """ Removes rows of a country if either Total GDP or GDP Per Capita 
        contain more than the threshold percentage of missing values.
        Returns a new dataframe.
        
    Args:
        df (Pandas dataframe): Expecting dataframe with outer index = []'Total GDP', 'GDP Per Capita', 'Gini Coeff']
                                inner index = [countries]
        threshold (float): a float between zero and one representing the percentage of nans above which the country is dropped.
    """
    assert (df.index.names[0] == 'Metric' and df.index.names[1] == 'Country'), "Unexpeced MultiIndex names. Expecting ['Metric', 'Countries]"
    assert (isinstance(threshold, float) & (0 <= threshold <= 1))

    df_copy = df.copy()
    valid_country_list = df.index.get_level_values('Country').unique().tolist()
    years_list = df.columns.tolist()

    print("********* DROPPING COUNTRIES **********")
    for country in valid_country_list:
        country_slice = df.xs(country, level='Country')
        country_gdp_nan_sum = pd.isna(country_slice.loc['Total GDP'].values).sum()
        country_gdp_percap_nan_sum = pd.isna(country_slice.loc['GDP Per Capita'].values).sum()
        if (country_gdp_nan_sum > len(years_list)*threshold) | (country_gdp_percap_nan_sum > len(years_list)*threshold):
            df_copy = df_copy.drop(country, level='Country')
            print("Dropping", country)
            print("  -  ", country_gdp_nan_sum, "missing values in Total GDP.")
            print("  -  ", country_gdp_percap_nan_sum, "missing values in GDP Per Capita.")
    print("***************************************")
    return df_copy




#################################################################

# User input validation

def check_years(years_list, start_year, end_year):

    start_year = start_year.strip()
    end_year = end_year.strip()

    years_in_list = (start_year in years_list) & (end_year in years_list)
    years_in_order = (int(end_year) > int(start_year))

    if not ((years_in_list) & (years_in_order)):
        raise KeyError("Invalid year range. Years must be in proper range, and start year must come before end year.")
    return


def describe_all(df):
    decade_list = [10 * (int(year) // 10) for year in df.columns]
    decade_list = [str(year) for year in decade_list]
    decade_list = pd.Series(decade_list).unique()

    for metric in df.index.get_level_values('Metric').unique():
        print(f"*** {metric} General Stats ***")
        print(df.loc[metric][decade_list].describe())

def check_country(country_list, new_country):

    new_country = new_country.strip()

    if not (new_country in country_list):
        raise KeyError("Country not in list. Try again.")
    return


def plotter(df, country_list, year_range, metric):
    idx = pd.IndexSlice
    sub_df = df.loc[idx[metric, :,country_list],idx[year_range[0]:year_range[-1]]]
    sub_df.transpose().plot() 
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    plt.show()



def get_user_input(combined_data):
    """ Gets the user input and checks that the input is a member of the specified data column. 
        Assumes the columns are years, and the rows are MultiIndexed [Metric, Country]

    Args:
        data_multi_index (Pandas DF): Pandas dataframe containing data for user input to be checked against.
        header (string): The header of the column to check for membership against the user input

    Raises:
        KeyError: If user input does not exist in specified header column.

    Returns:
        string: The valid user input value as an upper case string.
    """    
    
    years_list = combined_data.columns.tolist()

    while True:
        print("Enter a time frame to look at. Valid range is:", years_list[0], "to", years_list[-1])
        start_year = input("Start year: ")
        end_year = input("End year: ")
        try:
            check_years(years_list, start_year, end_year)
            break
        except KeyError as err:
            print(err)
            continue
    year_range = [start_year, end_year]        
    

    valid_country_list = combined_data.index.get_level_values('Country').unique().tolist()
    added_country_list = []
    count = 1
    while True:
        print("Enter a country to include in the analysis. Multiple countries may be added.")
        print("Enter 1 for a list of valid countries to enter")
        print("Enter 0 to analyze current list of countries.")
        user_input = input(f"Enter country number {count} : ")
        if user_input == '1':
            print(valid_country_list)
        elif user_input == '0':
            if count == 1:
                print("No countries added. Please add a country.")
                continue
            else:
                break
        try:
            check_country(valid_country_list, user_input)
            added_country_list.append(user_input)
            count += 1
            print(f"Current country list: {added_country_list}")
        except KeyError as err:
            print(err)
            print(f"Current country list: {added_country_list}")

            continue
    
    return (added_country_list, year_range)





    return




def main():


    print(os.getcwd())
    total_gdp = pd.read_csv("leprechaun_economics/total_gdp_us_inflation_adjusted.csv")
    total_gdp = total_gdp.set_index('country')

    gdp_percap = pd.read_csv("leprechaun_economics/gdppercapita_us_inflation_adjusted.csv")
    gdp_percap = gdp_percap.set_index('country')
    gini = pd.read_csv("leprechaun_economics/gini.csv")
    gini = gini.set_index('country')

    # make sorted copy of original raw data
    total_gdp_copy = total_gdp.sort_index().copy()
    gdp_percap_copy = gdp_percap.sort_index().copy()
    gini_copy = gini.sort_index().copy()
        
    # parse suffixes and convert values from strings to floats
    parse_gdp_values(total_gdp_copy)
    parse_gdp_values(gdp_percap_copy)
    # After parsing, force all columns to be numeric
    
    # Forces columns to numeric data instead of objects ( Code written by ChatGPT )
    year_cols = total_gdp_copy.columns.tolist()
    total_gdp_copy[year_cols] = total_gdp_copy[year_cols].apply(pd.to_numeric, errors='coerce')
    year_cols = gdp_percap_copy.columns.tolist()
    gdp_percap_copy[year_cols] = gdp_percap_copy[year_cols].apply(pd.to_numeric, errors='coerce')

    # Performs inner join on datasets and converts to MultiIndex Dataframe
    combined_data = df_index_inner_join(total_gdp_copy, gdp_percap_copy, gini_copy, 'Total GDP', 'GDP Per Capita', 'Gini Coeff')
    combined_data.index.names = ['Metric', 'Country']
    
    # Data Cleaning
    print("***************** Cleaning Data *******************")
    print("Original data size:", combined_data.shape)
    data_cleaned = drop_countries_by_nan(combined_data, 0.5)
    print("New data size:", data_cleaned.shape)
    print("***************************************************")

    # General Stats
    print("***************** General Stats *******************")
    describe_all(data_cleaned)

    # Data Processing
    print("***************** Data Processing *****************")
    # calculate gini dollars ( defined as GDP Per Capita * (1 - gini) )
    new_df = data_cleaned.loc['GDP Per Capita'] * (1 - data_cleaned.loc['Gini Coeff']/100)
    new_df.round()
    new_df.index = pd.MultiIndex.from_product([['Gini Dollars'], new_df.index], names=['Metric', 'Country'])

    print(data_cleaned.shape)
    print(new_df.shape)
    new_data_cleaned = pd.concat([data_cleaned, new_df])

    # Add new 'Classification' Index Level
    economic_weightclass = pd.cut(new_data_cleaned.loc['Total GDP',:]['2023'], bins=[0, 1e11, 1e12, 1e13, 1e14],labels=['Lightweight','Middleweight', 'Heavyweight', 'Superpower'])
    income_class = pd.cut(new_data_cleaned.loc['GDP Per Capita',:]['2023'], bins=[0, 1135, 4465, 13845, 40000, 300000],labels=['Low Income','Lower Middle Income', 'Upper Middle Income', 'High Income', 'Ultra High Income'])
    equality_class = pd.cut(new_data_cleaned.loc['Gini Coeff',:]['2023'], bins=[0, 30, 35, 40, 45, 50, 100],labels=['Very Low Inequality','Low Inequality', 'Low-Moderate Inequality', 'Moderate Inequality', 'Moderate-High Inequality', 'High Inequality'])
    livability_class = pd.cut(new_data_cleaned.loc['Gini Dollars',:]['2023'], bins=[0, 1135, 4465, 13845, 30000, 300000],labels=['Low Livability','Low-Moderate Livability', 'Moderate Livability', 'Moderate-High Livability', 'High Livability'])

    classification = pd.concat([economic_weightclass, income_class, equality_class, livability_class])
    metrics = new_data_cleaned.index.get_level_values('Metric')
    countries = new_data_cleaned.index.get_level_values('Country')

    # Use the classification series you created
    new_index = pd.MultiIndex.from_arrays([metrics, classification.values, countries], names=['Metric', 'Classification', 'Country'])

    # Assign to the DataFrame
    new_data_cleaned.index = new_index
    print(new_data_cleaned.shape)
    describe_all(new_data_cleaned)

    # user_input = get_user_input(data_cleaned)
    # print(user_input)

    test_input = (['Canada', 'Germany', 'Ireland', 'USA'], ['1960', '2023'])

    plotter(new_data_cleaned,test_input[0],test_input[1],'Total GDP')
    plotter(new_data_cleaned,test_input[0],test_input[1],'GDP Per Capita')
    plotter(new_data_cleaned,test_input[0],test_input[1],'Gini Coeff')
    plotter(new_data_cleaned,test_input[0],test_input[1],'Gini Dollars')





if __name__ == '__main__':
    
    main()