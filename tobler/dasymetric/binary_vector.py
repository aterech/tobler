import warnings
import sys
import geopandas as gpd

__all__ = ["binary_vector"]

def binary_vector(
    source_df,
    ancillary_df,
    population_columns,
    exclusion_column=None,
    exclusion_values=None,
):
    """Interpolates data within a source dataframe by overlaying it within an ancillary dataframe and excluding
    overlapping areas from final result. Fields and values from the ancillary dataset can be used to 
    determine the extent of the exclusion zone.

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        Source data used that will be impacted by the exclusion zone.
    ancillary_df : geopandas.GeoDataFrame
        Ancillary data used to construct the exclusion zone for the source_df.
    population_columns : list of str
        Columns from the source dataframe that will contain population data. Multiple columns can be specified.
    exclusion_column : str
        [Optional. Default=None] Column that can be used to construct a specific mask. If no column is specified, the entire
        ancillary dataframe will be used as a mask.
    exclusion_values : list of int
        [Optional. Default=None] Values from exclusion column that will be used to construct the mask. If no values are specified,
        the entire ancillary dataframe will be used as a mask.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with geometries matching the source_df, alongside the exclusion_column from ancillary_df

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

    # Erasing parts that intersect with the exclusion zone
    source = gpd.overlay(source,exclusion_zone,how='difference')

    #  Using union overlay to split areas with zero population away from the source df polygons
    zero_population = source.overlay(exclusion_zone,how='union')

    # Defining area of zero_population shapefile for final result output
    zero_population['area'] = zero_population.geometry.area

    if exclusion_column is not None:
        # Setting population to zero in areas part of exclusion zone
        zero_population.loc[zero_population[exclusion_column].isin(exclusion_values), population_columns] = 0

    # Creating final dataset and defining columns present
    binary_result = zero_population

    return binary_result
