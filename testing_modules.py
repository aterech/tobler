import geopandas as gpd
import matplotlib.pyplot as plt
import tobler
from tobler.dasymetric import extract_raster_features, masked_area_interpolate
from tobler.model import glm
from tobler.area_weighted import area_interpolate, area_join
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

results = area_interpolate(zip_code,philly,extensive_variables=['TotalPop'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('TotalPop',scheme='quantiles',cmap='viridis',ax=ax[0])
zip_code.plot(scheme='quantiles',cmap='viridis',ax=ax[1])

cax = plt.imshow(results['TotalPop'])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Total Population')
plt.colorbar(results.plot,cax,cmap='viridis',label='Population')

plt.show()


# Area join
joined = area_join(zip_code,philly,['ALAND20'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

joined.plot('ALAND20',scheme='quantiles',cmap='viridis',ax=ax[0])
philly.plot(scheme='quantiles',cmap='viridis',ax=ax[1])

cax = plt.imshow(joined['ALAND20'])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Total Area')
plt.colorbar(joined.plot,cax,cmap='viridis',label='Population')

plt.show()

# Extract raster features
land_cover_phl = extract_raster_features(zip_code,'C:/tobler/LandCover/LandCover.tif')

population_dist = masked_area_interpolate(source_df=zip_code,target_df=philly,raster=land_cover_phl,pixel_values=[21,22,23,24],extensive_variables=['TotalPop'])

fig, ax = plt.subplots(1,2, figsize=(14,7))

population_dist.plot('TotalPop',scheme='quantiles',cmap='viridis',ax=ax[0])
philly.plot(scheme='quantiles',cmap='viridis',ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Population Distribution')
plt.colorbar(population_dist.plot,cmap='viridis',label='Population')

plt.show()







