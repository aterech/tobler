import geopandas as gpd
import matplotlib.pyplot as plt
import tobler
from tobler.dasymetric import masked_area_interpolate
from tobler.model import glm
from tobler.area_weighted import area_interpolate
from libpysal.examples import load_example

crs = 2272

philly = gpd.read_file('PhilMegaFINA.shp').to_crs(crs)
zip_code = gpd.read_file('PHL_zipcode_2024.shp').to_crs(crs)

fig, ax = plt.subplots(1,2, figsize=(14,7))

philly.plot(ax=ax[0])
zip_code.plot(ax=ax[1])

for ax in ax:
    ax.axis('off')


# Areal interpolation, one thing I've noticed is you might need data from both datasets that contain population data

results = area_interpolate(source_df=philly, target_df=zip_code, intensive_variables=['TotalPop'], extensive_variables=['NonWPop'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('TotalPop', scheme='quantiles',  ax=ax[0])
zip_code.plot('Total_Pop', scheme='quantiles',  ax=ax[1])

ax[0].set_title('interpolated')
ax[1].set_title('original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Total Population')

plt.show()





