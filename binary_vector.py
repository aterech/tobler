from warnings import warn

import geopandas as gpd

from ..area_weighted import area_interpolate

__all__ = ["binary_vector"]


def binary_vector(
    source_df,
    target_df,
    ancillary_df,
    exclusion_field=None,
    exclusion_values=None,
    extensive_variables=None,
    intensive_variables=None,
    categorical_variables=None,
    allocate_total=True,
    n_jobs=-1,
    codes=None,
):
    """Interpolate data between two vector datasets using a third dataset that functions as an ancillary mask.
    Fields and values from the ancillary dataset can be used to determine the extent of the mask.

    Parameters
    ----------
    source_df : geopandas.GeoDataFrame
        source data to be converted to another geometric representation.
    target_df : geopandas.GeoDataFrame
        target geometries that will form the new representation of the input data
    ancillary_df : geopandas.GeoDataFrame
        ancillary data used to mask the source data. Ancillary dataframe can be the same as the target dataframe.
    exclusion_field : list
        [Optional. Default=None] Column from the ancillary data that will be used to determine mask extent.
        If no column is specified, the entire dataset will be used as a mask.
    exclusion_values : list of int
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
    #if codes:
    #    warn(
    #        "The `codes` keyword is deprecated and will be removed shortly. Please use `pixel_values` instead"
    #    )
    #    pixel_values = codes
    source_df = source_df.copy()
    assert not any(
        source_df.index.duplicated()
    ), "The index of the source_df cannot contain duplicates."

    #  create a column in the source_df to dissolve on
    idx_name = source_df.index.name if source_df.index.name else "idx"
    source_df[idx_name] = source_df.index

    #  clip source_df by its mask (overlay/dissolve is faster than gpd.clip here)
    source_df = gpd.overlay(
        source_df, ancillary_df.to_crs(source_df.crs), how="intersection"
    ).dissolve(idx_name)

    #  continue with standard areal interpolation using the clipped source
    interpolation = area_interpolate(
        source_df,
        target_df.copy(),
        extensive_variables=extensive_variables,
        intensive_variables=intensive_variables,
        n_jobs=n_jobs,
        categorical_variables=categorical_variables,
        allocate_total=allocate_total,
    )
    return interpolation
