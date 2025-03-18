from warnings import warn

import geopandas as gpd

from update.area_weighted import area_interpolate

__all__ = ["binary_vector"]


def binary_vector(
    source_df,
    ancillary_df,
    target_df=None,
    erase_ancillary=True,
    mask_field=None,
    mask_values=None,
    extensive_variables=None,
    intensive_variables=None,
    categorical_variables=None,
    allocate_total=True,
    n_jobs=-1,
):
    """Interpolate data between two vector datasets using a third dataset that functions as an ancillary mask.
    Fields and values from the ancillary dataset can be used to determine the extent of the mask.

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        source data to be converted to another geometric representation.
    ancillary_df : geopandas.GeoDataFrame
        ancillary data used to mask the source data. Ancillary dataframe can be the same as the target dataframe.
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


    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with geometries matching the target_df and extensive and intensive
        variables as the columns

    """
    
    # printing the CRS system (testing to make sure this pos actually remembers the crs)
    print(f'{mask_values}')
    print(f'{mask_field}')

    # add formula that uses specified exclusion columns and values to create the mask (optional code that only runs if something is specified)
    if mask_field:
        print("Mask field present")
        vector_mask = ancillary_df[ancillary_df[mask_field].isin(mask_values)]
        print(type(vector_mask))
        print(vector_mask.head())
    else:
        print("No mask field")
        vector_mask = ancillary_df.copy()
    
    print("vector_mask set")
    source_df = source_df.copy()
    assert not any(
        source_df.index.duplicated()
    ), "The index of the source_df cannot contain duplicates."

    # s

        

    #  create a column in the source_df to dissolve on
    idx_name = source_df.index.name if source_df.index.name else "idx"
    source_df[idx_name] = source_df.index

    #  clip source_df by its mask (overlay/dissolve is faster than gpd.clip here)
    if erase_ancillary == False:
        source_df_mask = gpd.overlay(
            source_df,vector_mask,how='difference',keep_geom_type=True
        )
 
    else:
        source_df_mask = gpd.overlay(
            source_df,vector_mask,how='intersection',keep_geom_type=True
        ).dissolve(idx_name)

    #  continue with standard areal interpolation using the clipped source
    if target_df is not None:
        interpolation = area_interpolate(
            source_df_mask,
            target_df.copy(),
            extensive_variables=extensive_variables,
            intensive_variables=intensive_variables,
            n_jobs=n_jobs,
            categorical_variables=categorical_variables,
            allocate_total=allocate_total,
        )
        return interpolation

    else:
        return source_df_mask