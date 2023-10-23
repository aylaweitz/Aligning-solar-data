# Aligning-solar-data
Techniques to read in and align IRIS, SDO, and Solar Orbiter/EUI data in Python.

## Aligning Solar Orbiter/EUI 174 data with AIA 171
### Initial datasets
- [`get_eui_data()`](https://github.com/aylaweitz/Aligning-solar-data/blob/38162d7a11319e921b8fcc0ce56dbe6879c54f37/load_data_functions.py#L6): using [SOAR](https://github.com/sunpy/sunpy-soar) to pull HRIEUV174 data and create an array of SunPy maps. 
- `get_aia_data()`: using AIA 171 data downloaded from [JSOC](http://jsoc.stanford.edu/ajax/lookdata.html?ds=aia.lev1_euv_12s) and create array of SunPy maps.

### Matching EUI and AIA in time
- Sort the EUI data by time.
- For each EUI SunPy map, find the AIA SunPy map that is closest in time. Recreate the AIA SunPy map array with these matched elements (this will include duplicates of AIA maps since EUI has a faster cadence).

### Correct for solar rotation
- Correct for solar rotation using SunPy -- method outlined [here](https://docs.sunpy.org/en/stable/generated/gallery/differential_rotation/reprojected_map.html).

### Align to same reference frame
- Use SunPy's [reproject_to](https://docs.sunpy.org/en/stable/generated/api/sunpy.map.GenericMap.html#sunpy.map.GenericMap.reproject_to) routine (we aligned all of our data to the middle IRIS observation).
   
### Manually aligning EUI observation with itself
There is some residual jitter in the EUI observation, so we used cross correlation to align the EUI observation with itself. We found that cross-correlating a moss region within our field of view gave the best results.

 - For each EUI image, cross-correlate a small and relatively stable region with the previous EUI image (we used [skimage.registration.phase_cross_correlation](https://scikit-image.org/docs/stable/api/skimage.registration.html#skimage.registration.phase_cross_correlation) for subpixel cross-correlation).
 - Apply the shifts so that each EUI image is aligned with the first EUI image (we used [scipy.ndimage.fourier_shift](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.fourier_shift.html)).

### Manually aligning EUI and AIA 171
The EUI observation is now self-consistent, but there is still some offset from AIA 171. We found cross-correlating the entire field of view gave the best results.

- For each matched EUI and AIA image (after matching the observations, eui_array[0] should correspond to aia_array[0]), cross-correlate with the entire field of view.
- Since the EUI and AIA pointings are stable, we calculate the mean shift value in x and y and apply that to each EUI image.

Now, HRIEUV174 and AIA 171 should be well aligned in temporally and spatially.
