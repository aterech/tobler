#tobler_testing.py

import geopandas as gpd
import matplotlib.pyplot as plt
import tobler
import rasterio
from tobler.dasymetric import extract_raster_features, masked_area_interpolate
from tobler.model import glm
from tobler.pycno import pycno_interpolate
from tobler.util import h3fy
from tobler.area_weighted import area_interpolate, area_join
from libpysal.examples import load_example
from quilt3 import Package

c1 = load_example('Charleston1')
c2 = load_example('Charleston2')

h1 = load_example('Hickory1')
h2 = load_example('Hickory2')

crs = 6569
tracts = gpd.read_file(c1.get_path('sc_final_census2.shp')).to_crs(crs)
zip_codes = gpd.read_file(c2.get_path('CharlestonMSA2.shp')).to_crs(crs)

fig, ax = plt.subplots(1,2, figsize=(14,7))

tracts.plot(ax=ax[0])
zip_codes.plot(ax=ax[1])

for ax in ax:
    ax.axis('off')
plt.show()


tracts['pct_poverty'] = tracts.POV_POP/tracts.POV_TOT


# Areal weighting
results = area_interpolate(source_df=tracts, target_df=zip_codes, intensive_variables=['pct_poverty'], extensive_variables=['EMP_MALE'])

area_interpolate


# Figure A of areal weighting
fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('EMP_MALE', scheme='quantiles',  ax=ax[0])
tracts.plot('EMP_MALE', scheme='quantiles',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Male Employment (extensive)')
plt.show()

# Figure B of areal weighting
fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[0])
tracts.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Poverty Rate (intensive)')
plt.show()


# Dasymetric mapping
p = Package.browse("rasters/nlcd", "s3://spatial-ucr")
p["nlcd_2011.tif"].fetch()

with rasterio.open('nlcd_2011.tif') as nlcd:
    profile = nlcd.profile
raster = extract_raster_features(tracts,'nlcd_2011.tif')

with rasterio.open('Charleston.tif','w',profile,'driver: GTiff') as save:
    save.write(raster,1)

results = masked_area_interpolate(raster='nlcd_2011.tif',
                                  source_df=tracts,
                                  target_df=zip_codes,
                                  pixel_values=[21,22,23,24],
                                  intensive_variables=['pct_poverty'],
                                  extensive_variables=['EMP_MALE'])

# Figure A from masked area interpolate
fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('EMP_MALE', scheme='quantiles',   ax=ax[0])
tracts.plot('EMP_MALE', scheme='quantiles',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Male Employment (extensive)')
plt.show()

# Figure B from masked area interpolate
fig, ax = plt.subplots(1,2, figsize=(14,7))

results.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[0])
tracts.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Poverty Rate (intensive)')
plt.show()


# GLM model-based
emp_results = glm(raster='nlcd_2011.tif',source_df=tracts, target_df=zip_codes, variable='EMP_MALE', )

fig, ax = plt.subplots(1,2, figsize=(14,7))

emp_results.plot('EMP_MALE', scheme='quantiles',  ax=ax[0])
tracts.plot('EMP_MALE', scheme='quantiles', ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Male Employment (extensive)')
plt.show()

# GLM model-based for poverty
pov_results = glm(raster="nlcd_2011.tif",source_df=tracts, target_df=zip_codes, variable='pct_poverty', )

fig, ax = plt.subplots(1,2, figsize=(14,7))

pov_results.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[0])
tracts.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[1])

ax[0].set_title('Interpolated')
ax[1].set_title('Original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Poverty Rate (Intensive)')
plt.show()

# Pycno-interpolation for EMP_MALE
pycno_result = pycno_interpolate(source_df=tracts,target_df=zip_codes,variables='EMP_MALE',cellsize=30)

fig, ax = plt.subplots(1,2, figsize=(14,7))

pycno_result.plot('EMP_MALE', scheme='quantiles',  ax=ax[0])
tracts.plot('EMP_MALE', scheme='quantiles', ax=ax[1])

ax[0].set_title('interpolated')
ax[1].set_title('original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Male Employment (extensive)')
plt.show()

# Pycno-interpolation for poverty pct
pov_pycno = pycno_interpolate(source_df=tracts,target_df=zip_codes,variables='pct_poverty',cellsize=30)

fig, ax = plt.subplots(1,2, figsize=(14,7))

pov_pycno.plot('EMP_MALE', scheme='quantiles',  ax=ax[0])
tracts.plot('EMP_MALE', scheme='quantiles', ax=ax[1])

ax[0].set_title('interpolated')
ax[1].set_title('original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Male Employment (extensive)')
plt.show()


# Hex-grid
hex_emp = h3fy(pov_results)

fig, ax = plt.subplots(1,2, figsize=(14,7))

hex_emp.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[0])
tracts.plot('pct_poverty', scheme='quantiles', cmap='magma',  ax=ax[1])

ax[0].set_title('interpolated')
ax[1].set_title('original')
for ax in ax:
    ax.axis('off')
fig.suptitle('Poverty Rate (intensive)')
plt.show()