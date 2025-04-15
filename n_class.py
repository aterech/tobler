import warnings
import sys
import geopandas as gpd
import pandas as pd
from update.area_weighted import area_interpolate

__all__ = ['percent_weighting']

def percent_weighting(
        source_df,
        ancillary_df,
        percent_field,
        percent_values,
        population_field,
        dissolve=True,
        weighting=1,
):
    """Interpolates data from a source dataframe using a class-weighted method. Each class is given a certain weighting
    that equals to 100% when combined. Areal interpolation can be completed if a target dataframe is specified.

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        source data to be converted to another geometric representation.
    ancillary_df : geopandas.GeoDataFrame
        ancillary data used to mask the source data. Ancillary dataframe can be the same as the target dataframe.
    percent_field : list
        Column from the ancillary dataframe that will be used to collect reclassified values.
    percent_values : list of int
        Values that will 
    target_df : geopandas.GeoDataFrame
        target geometries that will form the new representation of the input data (default will be None)
    erase_ancillary : bool
        Determines whether the ancillary dataframe will be used to remove sections that overlap with the source
        dataframe, or if it'll be used to only include overlapping sections. (default is True, which will erase
        overlapping sections)
    mask_field : list
        [Optional. Default=None] Column from the ancillary data that will be used to determine mask extent.
        If no column is specified, the entire dataset will be used as a mask.
    mask_values : list of int
        [Optional. Default=None] Values from the exclusion field that will be used for the mask.
    extensive_variables : list
        Columns of the input dataframe containing extensive variables to interpolate
    intensive_variables : list
        Columns of the input dataframe containing intensive variables to interpolate
    categorical_variables : list
        [Optional. Default=None] Columns in dataframes for categorical variables
    allocate_total : bool
        whether to allocate the total from the source geometries (the default is True).
    n_jobs : int
        [Optional. Default=-1] Number of processes to run in parallel to
        generate the area allocation. If -1, this is set to the number of CPUs
        available.
    parameters be set as a dictionary

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with geometries matching the target_df and extensive and intensive
        variables as the columns

    """

     # Checking CRS within dataframes to ensure they're matching
    crs_1 = source_df.crs
    crs_2 = ancillary_df.crs

    # If CRS are not matching, code exits safely
    if crs_1 != crs_2:
        warnings.warn('Source and ancillary CRS systems do not match. Exiting...', RuntimeWarning)
        return None

    # If CRS is geographic, a warning is shown but code doesn't exit
    if crs_1.is_geographic or crs_2.is_geographic:
        warnings.warn('Geographic CRS detected. Ensure all dataframes are in a projected CRS before continuing. Exiting...', RuntimeWarning)
    
    # Takes value from dictionary to determine total value of weighting
    #for value in percent_values.items():
    #    total_value = 0
    #    value.append(total_value)
    
    # If weighting is greater than 1, error is returned and code exits
    if value > 1:
        warnings.warn('Weighting exceeds 1. Check percent_values to ensure the weighting equals 1 or is less than 1. Exiting...', RuntimeWarning)
        return None
    
    # Creating copies of shapefiles
    source = source_df.copy()
    ancillary = ancillary_df.copy()

    # Retrieving source area and index
    source['area'] = source.geometry.area
    ancillary['area'] = ancillary.geometry.area

    # Defining keys and new column 'weighting'
    for key, value in percent_values.items():
        ancillary.loc[ancillary[percent_field]== key, 'weighting']=value
        print(f'Value: {key}, Weight: {value}')
    
    # Ensuring that population field is integer before proceeding
    #if isinstance(population_field,int) == False:
    #    population_field = source[population_field].astype(int)

    if dissolve == True:
        ancillary = ancillary.dissolve(by=percent_field)

    # Intersecting the source and ancillary dataframes
    intersect = gpd.overlay(source,ancillary,how='intersection')

    # Defining the population within a specified class by population field and weighting
    intersect['class_pop'] = intersect[population_field] * intersect['weighting'] / weighting

    # Defining new column 'class_area' to contain area of each matching value
    intersect['class_area'] = intersect.geometry.area

    # Exploding multi polygons within dataset to single polygons
    intersect = intersect.explode()

    # Defining another new column 'area' to contain area of each separate polygon 
    intersect['area'] = intersect.geometry.area

    # Dividing the area by the class area to determine percentage the polygon constitutes of total area
    intersect['percent'] = intersect['area'] / intersect['class_area']

    # Multiplying class population by the percentage to determine the total population
    intersect['total_pop'] = intersect['class_pop'] * intersect['percent']

    # Defining ancillary df as result to return the final results
    result = intersect[[percent_field,'weighting','class_pop','total_pop',]]

    # Returning result
    return result

    
