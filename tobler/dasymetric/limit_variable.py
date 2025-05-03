from warnings import warn
import geopandas as gpd
import pandas as pd

__all__ = ["limit_variable"]

def  limit_variable(source_df, 
               ancillary_df, 
               aclass, 
               dclass, 
               cols_intp = [None]
):
 """
    Interpolates data provided by user into disaggregated polygons through the limiting variable method. If the user provides a populated dclass parameter,
    then data is interpolated based on user provided threshold per individual area class. Remaining data is then further interpolated into areas with other classes that
    have an unlimited threshold. If the user does not provide a populated dclass parameter, the code performs a simple interpolation based on proportional weight.
 
    Parameters
    ----------
    source_df : DataFrame
        Dataframe that contains columns/values user intends to interpolate.
    ancillary_df : DataFrame
        DataFrame where area-class categories are housed.
    aclass : str
        Column that user identifies as containing the area-class categories
    dclass : dict
        Area-class categories with assigned thresholds per square unit (in value: threshold format). 
    cols_intp : list
        Column from source dataframe intended for interpolation.
    Returns
    -------
    output_df : GeoDataFrame
        Target dataframe with results housed in 'results_intp' column.
    """
 
 #Prepare geometries by removing overlapping or self intersecting polygons 
 source_df.make_valid()
 ancillary_df.make_valid()

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
 
 #Calculate the area of source polygon
 print("Source area columns populating...")
 source_df['area_source'] = source_df.geometry.area
 print("Source area calculated")

 #Reindex df
 print("Source df reindexing...")
 source_df['_index'] = source_df.index
 print("Source index reindexed")

 #Perform intersection of source and ancillary DF
 print("Performing overlay of DFs (How=Intersection)...")
 output_df = gpd.overlay(source_df, ancillary_df, how = 'intersection')
 print("Overlay complete")

 #Calculate intersected polygons area
 print("Intersect areas calculating...")
 output_df['area_intersect'] = output_df.geometry.area
 print("Intersect area calculated")

 #Calculate sum of all intersected areas (assign as equal value per row)
 sum_inter = output_df.groupby('_index')['area_intersect'].sum()
 sum_inter.rename('sum_inter', inplace = True)
 output_df = output_df.merge(sum_inter, on = '_index') 
 print("Sum per zone calculated")

 #Calculate Proportional Weight
 output_df['prop_wt'] = output_df['area_intersect'] / output_df['sum_inter']
 print("Prop weight calculated")

 #Assign thresholds to area classes
 print("assigning thresholds to area classes")
 for key, value in dclass.items():
    output_df.loc[output_df[aclass]== key, 'threshold']=value

 #Create column for interpolation
 output_df['result_intp'] = 0

 if dclass != {}:
    #Get list of keys that is user provided in dclass parameters
    key_list = [key for key in dclass]
    print("Key list created")
    
    #Interpolate cols_intp column with proportional weight * column to be interpolated
    output_df['result_intp'] = output_df.apply(lambda row: row['prop_wt'] * row[cols_intp] if row[aclass] in key_list else row['result_intp'], axis = 1)

    #Use clip function to assign maximum amount of results_intp column
    output_df['result_intp'] = output_df['result_intp'].clip(upper = output_df['threshold'] * output_df['area_intersect'])
    
    #Create column to house area associated with polygons that have thresholds
    output_df['area_int_thresh'] = 0

    output_df['area_int_thresh'] = output_df.apply(lambda row: row['area_intersect'] if row[aclass] in key_list else row['area_int_thresh'], axis = 1)

    #Sum the area of intersecting polygons that have thresholds
    area_int_thresh_sum = output_df.groupby('_index')['area_int_thresh'].sum()
    area_int_thresh_sum.rename('area_int_thresh_sum', inplace=True)
    output_df = output_df.merge(area_int_thresh_sum, on = '_index')

    #Minus calculated area from original area sum of intersecting polygons
    output_df['area_diff'] = output_df.apply(lambda row: row['sum_inter'] - row['area_int_thresh_sum'], axis=1)

    #Sum the amount of cols_intp value per zone that has been used
    cintp_thresh_sum= output_df.groupby('_index')['result_intp'].sum()
    cintp_thresh_sum.rename('cintp_thresh_sum', inplace = True)
    output_df = output_df.merge(cintp_thresh_sum, on = '_index')

    #Minus calculated value from original cols_intp value that will be distributed amongst remaining polygons
    output_df['remain_intp'] = output_df.apply(lambda row: row[cols_intp] - row['cintp_thresh_sum'], axis = 1)

    #Redefine proportional weight
    output_df['prop_wt'] = output_df.apply(lambda row: row['area_intersect'] / row['area_diff'] if row[aclass] not in key_list else row['prop_wt'], axis = 1)

    #Interpolate throws with unlimited class or no threshold
    output_df['result_intp'] = output_df.apply(lambda row: row['prop_wt'] * row['remain_intp'] if row[aclass] not in key_list else row['result_intp'], axis=1)

    #Delete unnecessary columns
    del output_df['sum_inter']
    del output_df['area_int_thresh']
    del output_df['area_int_thresh_sum']
    del output_df['cintp_thresh_sum']
    del output_df['remain_intp']
    del output_df['area_diff']


 else:

    #If no dclass defined, do simple interpolation of prop. weight * count
    output_df['result_intp'] = output_df.apply(lambda row: row['prop_wt'] * row[cols_intp], axis = 1)

    #Delete unnecessary columns
    del output_df['sum_inter']
    
 print("Results housed in result_intp column")

 return output_df

