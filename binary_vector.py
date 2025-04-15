import warnings
import sys
import geopandas as gpd
from update.area_weighted import area_interpolate

__all__ = ["binary_vector"]



def binary_vector(
    source_df,
    ancillary_df,
    population_columns,
    exclusion_column=None,
    exclusion_values=None,
):
    """Interpolate data between two vector datasets using a third dataset that functions as an ancillary mask.
    Fields and values from the ancillary dataset can be used to determine the extent of the mask.

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        source data to be converted to another geometric representation.
    ancillary_df : geopandas.GeoDataFrame
        ancillary data used to mask the source data. Ancillary dataframe can be the same as the target dataframe.
    mask_field : list
        [Optional. Default=None] Column from the ancillary data that will be used to determine mask extent.
        If no column is specified, the entire dataset will be used as a mask.
    mask_values : list of int
        [Optional. Default=None] Values from the exclusion field that will be used for the mask.

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

    # Creating copies of source and ancillary dfs
    source = source_df.copy()
    ancillary = ancillary_df.copy()

    # If exclusion column and values are specified, create an exclusion zone using them
    if exclusion_column is not None:
        print("Exclusion field present")
        exclusion_zone = ancillary[ancillary[exclusion_column].isin(exclusion_values)]

    # If neither are specified, entire ancillary df is used as an exclusion zone
    else:
        print("No exclusion field specified")
        exclusion_zone = ancillary
    
    # Dissolving polygons part of the exclusion zone into 1 polygon
    exclusion_zone = exclusion_zone.dissolve()

    #  Using union overlay to split areas with zero population away from the source df polygons
    zero_population = source.overlay(exclusion_zone,how='union')

    # Converting columns into strings if they are a tuple or object
    #if isinstance(zero_population[exclusion_column],str) == False: 
    #    zero_population[exclusion_column] = zero_population[exclusion_column].astype(str)
    
    #if isinstance(source_df[population_columns],str) == False:
    #    source_df[population_columns] = source_df[population_columns].astype(str)

    # Defining area of zero_population shapefile for final result output
    zero_population['area'] = zero_population.geometry.area

    # Setting population to zero in areas part of exclusion zone
    zero_population.loc[zero_population[exclusion_column].isin(exclusion_values), population_columns] = 0

    # Creating final dataset and defining columns present
    binary_result = zero_population[[population_columns, 'area']]

    return binary_result