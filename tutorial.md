# Overview of Tobler's New Dasymetric Functions

This tutorial will cover 3 new functions added to the tobler package and can be accessed under tobler.dasymetric. The 3 functions are:
- binary_vector
- limit_variable
- percent_weighting

## Importing extensions and shapefiles

Let's suppose that we want to determine population distribution within a specific portion of the city of Philadelphia. We can do this with each of the 3 dasymetric functions. First, let's import all the needed extensions for this tutorial.

### Extensions
``` 
import geopandas as gpd
import matplotlib.pyplot as plt
from tobler.dasymetric import binary_vector, limit_variable, percent_weighting
```

After importing all of our needed extensions, we can also import our shapefiles via geopandas. In the meantime, let's also set both shapefiles to the same CRS to the study area by defining our CRS ID with variable crs and using to_crs(). Note that all 3 functions will trigger warnings if any input shapefiles don't have matching CRS.

### Shapefiles
```
crs = 2272
census = gpd.read_file("Census_South/Census_South.shp").to_crs(crs)
land_use = gpd.read_file("Land_Use_South/Land_Use_South.shp).to_crs(crs)
```

## Binary method

The first function is the binary method, referred to as binary_vector within the Tobler package. This method takes 2 vector shapefiles (a source dataframe and ancillary dataframe), using the latter shapefile as an exclusion zone to remove sections of the source dataframe that overlap with the exclusion zone. Polygons within an exclusion zone will revert their population fields to zero, with polygons located outside maintaining their population data. This method is particularly useful when trying to remove population data from certain land uses including water, transportation, or undeveloped polygons. 

In the binary_vector function, the exclusion zone can be constructed in 2 different ways. The first approach is to use the entire ancillary dataframe as an exclusion zone, removing any soource polygons that overlap with the exclusion zone. Another approach allows the user to construct an exclusion zone using certain parts of the ancillary dataframe instead of the entire dataset. This approach can be helpful in cases where numerous types of land use patterns are contained within a dataframe.

```
result = binary_vector(source_df=census,ancillary_df=land_use,population_columns="Population",exclusion_column="C_DIG1",exclusion_values=[5,7,8])
```
The code above is an example of how the user can utilize the binary_vector function. In the example, our census tract shapefile is used as the source dataframe, with our land use shapefile being used as the ancillary dataframe. The population column used is a column named "Population" that is located within the census tract shapefile. Population columns should be derived from the source dataframe, and multiple columns can be passed through as a list. 

The final 2 parameters are dedicated for constructing the exclusion zone. The exclusion column parameter asks for a column within the ancillary dataframe, observing which rows within the exclusion column contain a specified exclusion value. The specified values withi exclusion_values will be used to construct the exclusion zone. In this example, we utilized "C_DIG1", a column containing the land use classes within Philadelphia, as our exclusion column. Values 5, 7, and 8 (Which represent transportation, water, and park polygons respectively) are used as exclusion values. 

If the entire ancillary df is used as an exclusion zone, exclusion_column and exclusion_values are optional and shouldn't be used. 


## Limiting variable
```
result = 
```

## N-Class method

The third and final function is based on the n-class method, known as percent_weighting in Tobler, which allocates population data in a similar way to limiting variable. The main difference is that instead of specified thresholds, n-class dedicates a specific weighting to each value using a dictionary. The weighting is utilized to determine the percentage of the population within a source dataframe that should be allocated to the specified value. This number is then further trimmed down by calculating the area the polygon takes up, allocating higher population numbers to larger polygons. The standard number of specified values within n-class is normally 3 classes, however there is no limit to how many classes can be specified within the dictionary as long as the total weighting doesn't exceed 1. In the cases where total_weighting is below 1, the remaining percentage is allocated to values not included in the dictionary.
```
result = percent_weighting(source_df=census,ancillary_df=land_use,percent_field="C_DIG1",percent_values={1:0.75,2:0.15,5:0,8:0},population_field="Population")
```
In the above example, the assigned dictionary will allocate 75% of population data within each census tract to residential polygons, 15% to commercial polygons, and allocate zero population to transportation and water polygons. With this dictionary, only 90% of the population data is assigned and the remaining 10% will be allocated to other polygons. In addition, a boolean parameter called "dissolve" is also utilized to determine whether neighboring polygons of the same value should be dissolved into 1 polygon. The option is set to True by default, and doesn't need to be specified unless the user wants to prevent the polygons from dissolving.
