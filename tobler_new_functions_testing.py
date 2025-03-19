#tobler_new_functions.py

import geopandas as gpd
import matplotlib.pyplot as plt
import tobler
import rasterio
from tobler.dasymetric import extract_raster_features, masked_area_interpolate
from tobler.model import glm
from tobler.pycno import pycno_interpolate
from tobler.area_weighted import area_interpolate
from tobler.util import h3fy
from update.dasymetric.binary_vector import binary_vector
from libpysal.examples import load_example
from shapely.validation import make_valid
from quilt3 import Package

crs = 2272
blk_groups = gpd.read_file('Block_Groups/Block_Groups_2010.shp').to_crs(crs)
traffic = gpd.read_file('Traffic/Traffic_Accidents.shp').to_crs(crs)
land_use = gpd.read_file('Land_Use_2/Land_Use_2.shp').to_crs(crs)
ppr = gpd.read_file('PPR_Properties/PPR_Properties.shp').to_crs(crs)
empowerment_zone = gpd.read_file('Empowerment_Zones/PhiladelphiaEmpowermentZones201201.shp').to_crs(crs)

# fig, ax = plt.subplots(1,2, figsize=(14,7))

# land_use.plot(ax=ax[0])
# traffic.plot(ax=ax[1])

# for ax in ax:
#     ax.axis('off')
# plt.show()

# results = area_interpolate(source_df=traffic,target_df=blk_groups,extensive_variables=['Count_'])

# fig, ax = plt.subplots(1,2, figsize=(14,7))

# results.plot('Count_', scheme='quantiles',cmap='Reds',  ax=ax[0])
# traffic.plot('Count_', scheme='quantiles',cmap='Reds',  ax=ax[1])

# ax[0].set_title('Interpolated')
# ax[1].set_title('Original')
# for ax in ax:
#     ax.axis('off')
# fig.suptitle('Crash Count')
# plt.show()


 # Binary method
mask = binary_vector(source_df=traffic,ancillary_df=empowerment_zone,erase_ancillary=True,extensive_variables=['Count_'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

mask.plot('Count_',scheme='quantiles',cmap='Reds', ax=ax[0])
empowerment_zone.plot(scheme='quantiles',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Crash Count')
plt.show()

results2 = binary_vector(source_df=traffic,ancillary_df=land_use,erase_ancillary=False,mask_field='C_DIG1',mask_values=[7],extensive_variables=['Count_'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

results2.plot(scheme='quantiles',cmap='Reds',  ax=ax[0])
traffic.plot(scheme='quantiles',cmap='Reds',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Crash Count')
plt.show()


validity = land_use.is_valid

print(validity)

new_valid = make_valid(land_use)

print(new_valid.value_counts())

invalid_geometries = land_use[~validity]
print(invalid_geometries.head())

invalid_geometry_list = invalid_geometries['geometry'].tolist()
print(invalid_geometry_list)

