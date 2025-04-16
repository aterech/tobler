from warnings import warn
import geopandas as gpd
import pandas as pd

__all__ = ["limit_var"]

def  limit_var(source_df, 
               ancillary_df, 
               aclass, dclass, 
               cols_intp = [None]
):
 """
    Interpolates data provided by user in source into disaggreted polygons. Polygons that are within the 
    possible values for area class categories are assigned a threshold as specified by the user. Polygons
    that are not within the area class are assigned zero.
 
    Parameters
    ----------
    source_df : DataFrame
        Dataframe that contains columns/values user intends to interpolate.
    ancillary_df : DataFrame
        DataFrame that contains area-class categroies.
    aclass : str
        Column user wants to use for Area-class categoies.
    dclass : dict
        Area-class categories with assigned thresholds per square unit (in value: threshold format). 
    cols_intp : list
        Column from source dataframe intended for interpolation.
    Returns
    -------
    output_df : DataFrame
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

 #Calculate Areal Weight (intersect area/source area)
 output_df['areal_weight'] = output_df['area_intersect'] / output_df['area_source']

 #Assign thresholds to area classes
 print("assigning thresholds to area classes")
 for key, value in dclass.items():
    output_df.loc[output_df[aclass]== key, 'threshold']=value

 #Create columns for interpolation
 output_df['result_intp'] = 0

 output_df['result_intp_copy'] = 0 #Copy is necessary here for lambda value in interpolation section

 #If warning if dclass is empty

 if dclass == {}:
   
   warn("Class dictionary (dclass) is empty. No interpolation performed.")

 #else clause if class dictionary thresholds are specified

 else:
   
   #Conduct the interpolation (Formula = Areal weight * cols_intp)

   key_list = [key for key in dclass]
 
   output_df['result_intp'] = output_df.apply(lambda row: row['areal_weight'] * row[cols_intp] if row[aclass] in key_list else row['result_intp'], axis = 1)

   output_df['result_intp_copy'] = output_df['result_intp']

   print("Interpolation Complete")

   #If interpolated value exceeds threshold, row gets threshold density (Formula = area intersect * threshold)

   output_df['result_intp'] = output_df.apply(lambda row: row['area_intersect'] * row['threshold'] if row['result_intp_copy'] > row['threshold'] else row['result_intp'], axis = 1)

   print("Interpolation for higher threshold rows calculated")

   #Delete unnecessary column

   del output_df['result_intp_copy'] 

   print("Excess column deleted")


 print("Interpolated values stored in result_intp column")

 output_df = output_df[['geometry', aclass, 'result_intp']]

 return output_df


