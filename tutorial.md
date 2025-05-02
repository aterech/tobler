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

After importing all of our needed extensions, we can also import our shapefiles: Census_South and Land_Use_South. In the meantime, let's also set both shapefiles to the same CRS to the study area. Note that all 3 functions will trigger warnings if any input shapefiles don't have matching CRS.

### Shapefiles
```
census = gpd.read_file("Census_South/Census_South.shp").to_crs(crs)
land_use = gpd.read_file("Land_Use_South/Land_Use_South.shp).to_crs(crs)
```

## Binary method

```
result = binary_vector(source_df=census,ancillary_df=land_use,population_columns="Population",exclusion_column="C_DIG1",exclusion_values=[5,7,8])
```


## Limiting variable
```
result = 
```

## N-Class method
```
result = percent_weighting(source_df=census,ancillary_df=land_use,percent_field="C_DIG1",percent_values={1:0.75,2:0.15,5:0,8:0},population_field="Population")
```
