import warnings
import sys
import geopandas as gpd

__all__ = ['percent_weighting']

def percent_weighting(
        source_df,
        ancillary_df,
        percent_field,
        percent_values,
        population_field,
        dissolve=True,
):
    """Interpolates data from a source dataframe using a class-weighted method. Each class is given a certain weighting
    that equals up to 100% when combined, which is used to redistribute population data based on the weighting attributes. 

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        Source dataframe containing population data.
    ancillary_df : geopandas.GeoDataFrame
        Ancillary dataframe containing field where weighting values will be used to reallocate data.
    percent_field : str
        Column from the ancillary dataframe that will be used to collect reclassified values.
    percent_values : dict
        Values that will be contained in a dictionary, with the key referring to the variables within the percent field,
        and the value referring to the weighting percentage  
    population_field : str 
        Field that contains the population values from the source dataframe. Only one population field can currently be run in a function.
    dissolve : bool
        [Default=True] A boolean parameter that determines whether ancillary polygon boundaries will be dissolved. The default option dissolves the boundaries.
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with source_df geometries and reallocated population data

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
    total_value = 0
    for key, value in percent_values.items():
        total_value = total_value + value
    
        # If weighting is greater than 1, error is returned and code exits
        if total_value > 1:
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

    # Unallocated value is determined by subtracting 1 and the total value
    unallocated = 1 - total_value
    unallocated_value = round(unallocated,2)

    # Assigns the unallocated value to remaining rows
    ancillary.loc[ancillary['weighting'].isna(), 'weighting']=unallocated_value

    # This section of code runs if dissolve option is false
    if dissolve == False:
        ancillary_no_dissolve = ancillary.dissolve(by=percent_field)

        # Intersecting the source and ancillary dataframes
        no_dissolve = gpd.overlay(source,ancillary_no_dissolve,how='intersection')
        intersect = gpd.overlay(source,ancillary,how='intersection')

        # Defining new column 'class_area' to contain area of each matching value
        no_dissolve['class_area'] = no_dissolve.geometry.area

        # Setting up apply function to allocate data from 'class_area' column to the correct polygons
        intersect['class_area'] = intersect.apply(lambda x: no_dissolve[no_dissolve.geometry.contains(x.geometry)]['class_area'].iloc[0] if not no_dissolve[no_dissolve.contains(x.geometry)].empty else None, axis=1)

        # If weighting from dictionary doesn't add up to 1, remaining data will be allocated to polygons outside the dictionary
        if total_value != 1:
            # Creating unallocated zone to only include unallocated polygons
            unallocated_zone = no_dissolve[no_dissolve.apply(lambda x: x['weighting'] == unallocated_value, axis=1)]
            unallocated_area = unallocated_zone.dissolve()
            total = gpd.overlay(source,unallocated_area,how='intersection')

            # Defining class_area based on the area of unallocated polygons 
            total['class_area'] = total.geometry.area

            intersect['class_area'] = intersect.apply(lambda x: total[total.geometry.contains(x.geometry)]['class_area'].iloc[0] if x['weighting'] == unallocated_value and not total[total.geometry.contains(x.geometry)].empty else x['class_area'], axis=1)

        # Defining another new column 'area' to contain area of each separate polygon 
        intersect['area'] = intersect.geometry.area

        # Defining the population within a specified class by population field and weighting
        intersect['class_pop'] = intersect[population_field] * intersect['weighting']

        # Dividing the area by the class area to determine percentage the polygon constitutes of total area
        intersect['percent'] = intersect['area'] / intersect['class_area']

        # Multiplying class population by the percentage to determine the total population
        intersect['total_pop'] = intersect['class_pop'] * intersect['percent']

        # Defining ancillary df as result to return the final results
        result = intersect

        # Returning result
        return result

    # If dissolve option is true, this section of code runs
    if dissolve == True:
        ancillary = ancillary.dissolve(by=percent_field)

        # Intersecting the source and ancillary dataframes
        intersect = gpd.overlay(source,ancillary,how='intersection')

        # Defining new column 'class_area' to contain area of each matching value
        intersect['class_area'] = intersect.geometry.area

        # Exploding multi polygons within dataset to single polygons
        intersect = intersect.explode()

        # If weighting from dictionary doesn't add up to 1, remaining data will be allocated to polygons outside the dictionary
        if total_value != 1:
            # Creating unallocated zone to only include unallocated polygons
            unallocated_zone = intersect[intersect.apply(lambda x: x['weighting'] == unallocated_value, axis=1)]
            unallocated_area = unallocated_zone.dissolve()
            total = gpd.overlay(source,unallocated_area,how='intersection')

            # Defining class_area based on the area of unallocated polygons 
            total['class_area'] = total.geometry.area

            # Use lambda function to assign class_area to rows containing the unallocated value
            intersect['class_area'] = intersect.apply(lambda x: total[total.geometry.contains(x.geometry)]['class_area'].iloc[0] if x['weighting'] == unallocated_value and not total[total.geometry.contains(x.geometry)].empty else x['class_area'], axis=1)

        # Defining another new column 'area' to contain area of each separate polygon 
        intersect['area'] = intersect.geometry.area

        # Defining the population within a specified class by population field and weighting
        intersect['class_pop'] = intersect[population_field] * intersect['weighting']

        # Rounding values from 'class_pop' to whole numbers
        intersect['class_pop'] = intersect['class_pop'].round()

        # Dividing the area by the class area to determine percentage the polygon constitutes of total area
        intersect['percent'] = intersect['area'] / intersect['class_area']

        # Multiplying class population by the percentage to determine the total population
        intersect['total_pop'] = intersect['class_pop'] * intersect['percent']

        # Rounding the population column to hundredths
        intersect['total_pop'] = intersect['total_pop'].round(2)

        # Defining ancillary df as result to return the final results
        result = intersect

        # Returning result
        return result
