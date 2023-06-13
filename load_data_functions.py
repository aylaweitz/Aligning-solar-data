from imports import *

############ PULLING / READING IN DATA AS SUNPY MAPS ############

# GET EUI HRIEUV174 L2 DATA -- ONLY WORKS ON LMSAL WIFI FOR SOME REASON?
def get_eui_data(start_date, end_date):
    """Pull EUI HRIEUV174 fits files using SOAR (https://github.com/sunpy/sunpy-soar) and create array of SunPy maps

    Parameters
    ----------
    start_date: str
        search window for observations begins at this time

    end_date: str
        search window for observations ends at this time

    Returns
    -------
    eui_maps: np.array
        found EUI observations as array of SunPy maps
    """
    instrument = a.Instrument('EUI')
    time = a.Time(start_date, end_date)
    level = a.Level(2)
    product = a.soar.Product('EUI-HRIEUV174-IMAGE')

    result = Fido.search(instrument & time & level & product)
    # print(len(result))
    files = Fido.fetch(result)

    # make array of EUI SunPy map objects
    eui_map_array = np.array(sunpy.map.Map(files))

    # divide each data array by exposure time
    norm_eui_map_array = np.empty(len(eui_map_array), dtype=type(eui_map_array[0]))
    for i, elem in tqdm(enumerate(eui_map_array)):

        # normalize data by exposure time
        norm_data = normalize_data(elem.data, elem.meta['XPOSURE'])

        meta = elem.meta # get metadata
        norm_eui_map_array[i] = sunpy.map.Map((norm_data, meta)) # recreate sunpy map

    return norm_eui_map_array


# GET IRIS DATA
def get_iris_data(filename):
    """Read in IRIS data from local file and create array of SunPy maps

    Parameters
    ----------
    filename: str
        filename of IRIS data to read in

    Returns
    -------
    iris_map_array: np.array
        IRIS observations as array of SunPy maps
    """
    hdul = fits.open(filename)
    
    # get header info
    header = hdul[0].header
    
    aux = hdul[1].data # auxillary metadata
    aux_hd = hdul[1].header
    
    # get timing of observation -- https://iris.lmsal.com/itn45/IRIS-LMSALpy_chapter6.html?highlight=timing#time-of-observations-and-exposure-times
    time_diff = aux[:, aux_hd['TIME']]
    times = np.datetime64(header['DATE_OBS']) + time_diff * np.timedelta64(1, 's')
    
    # LOOP THROUGH AND CREATE SunPy maps for each
    iris_map_array = np.empty(len(hdul[0].data), dtype=sunpy.map.sources.iris.SJIMap)

    for i in tqdm(range(len(hdul[0].data))):

        one_data = hdul[0].data[i]
        
        # change 'DATE_OBS' value in header since that it what SunPy will read as the time
        time = times[i]
        header['DATE_OBS'] = str(time)

        # normalize data
        norm_data = normalize_data(one_data, header['EXPTIME'])

        iris_map = sunpy.map.Map((norm_data, header))
        iris_map_array[i] = iris_map

    # iris_maps = whole_obs(iris_map_array, 'IRIS')

    return iris_map_array


# GET AIA DATA
def get_aia_data(folder):
    """Read in AIA data (downloaded from JSOC) from local file and create array of SunPy maps

    Parameters
    ----------
    folder: str
        folder of AIA data to read in

    Returns
    -------
    aia_map_array: np.array
        AIA observations as array of SunPy maps
    """

    # USING DATA DOWNLOADED FROM JSOC
    aia_map_array = np.array(sunpy.map.Map(folder + '/*.fits'))

    aia_new_maps = []
    for one_map in tqdm(aia_map_array):
        
        new_map = sunpy.map.Map(one_map.data, one_map.fits_header) # keeping just header (not all the metadata) bc won't allow me to make pickles with full metadata
        aia_new_maps.append(new_map)

    # READING AIA DATA DOWNLOADED FROM IRIS WEBSITE
    # hdul = fits.open(filename)
    # header = hdul[0].header

    # aux = hdul[1].data # auxillary metadata
    # aux_hd = hdul[1].header

    # time_diff = aux[:, aux_hd['TIME']]
    # times = np.datetime64(header['DATE_OBS']) + time_diff * np.timedelta64(1, 's')

    # # LOOP THROUGH AND CREATE OBJECTS FOR EACH 
    # aia_map_array = np.empty(len(hdul[0].data), dtype=sunpy.map.sources.AIAMap)
    # for i in tqdm(range(len(hdul[0].data))):
        
    #     one_data = hdul[0].data[i]
            
    #     # change 'DATE_OBS' value in header since that it what SunPy will read as the time
    #     time = times[i]
    #     header['DATE_OBS'] = str(time)
        
    #     # add in "WAVELNTH" to header because it's not there for some AIA channels for some reason?
    #     header['WAVELNTH'] = '171.0 Angstrom'

    #     # normalize data with exposure time
    #     norm_data = normalize_data(one_data, header['EXPTIME'])

    #     time = times[i]
    #     aia_map = sunpy.map.Map((norm_data, header))

    #     # create IRIS object and append to array
    #     aia_map_array[i] = aia_map

    # # TRYING TO GET DATA WITH SOAR -- GETTING "ConnectionError: No online VSO mirrors could be found."
    # instrument = a.Instrument('AIA')
    # # time = a.Time(start_date, end_date)
    # time = a.Time('2022-03-05', '2022-03-06')
    # wavelength = a.Wavelength(171*u.angstrom)

    # result = Fido.search(instrument & time & wavelength)
    # print(len(result))
    # files = Fido.fetch(result)

    # # make array of EUI SunPy map objects
    # aia_map_array = np.array(sunpy.map.Map(files))

    return aia_new_maps


def get_hmi_data(folder):
    """Read in HMI data (downloaded from JSOC) local folder and create array of SunPy maps

    Parameters
    ----------
    folder: path, str
        folder where HMI fits files are located (downloadd from JSOC)

    Returns
    -------
    hmi_map_array: np.array
        HMI observations as array of SunPy maps
    """
    # data downloaded from JSOC is location in "folder"
    hmi_map_array = np.array(sunpy.map.Map(folder + '/*.fits')) # turn each fits file in this folder into a SunPy Map


    # TRYING TO GET DATA WITH SOAR -- GETTING "ConnectionError: No online VSO mirrors could be found."

    # https://docs.sunpy.org/en/stable/guide/acquiring_data/jsoc.html
    # time = a.Time(start_date, end_date)
    # time = a.Time('2022-03-05', '2022-03-06')
    # series = a.jsoc.Series('hmi.synoptic_mr_polfil_720s') #hmi.M_45s

    # # https://docs.sunpy.org/en/stable/generated/gallery/acquiring_data/downloading_hmi.html

    # result = Fido.search(time, a.jsoc.Series('hmi.v_45s'))
    # files = Fido.fetch(result)

    # # make array of EUI SunPy map objects
    # hmi_map_array = np.array(sunpy.map.Map(files))

    return hmi_map_array


# NORMALIZE DATA
def normalize_data(data, exposure):
    """Normalize data by dividing by exposure time.

    Parameters
    ----------
    data: np.array
        data to normalize
    exposure: float
        exposure time

    Returns
    -------
    np.array, normalize data
    """
    return data / exposure


# SORT DATA BY TIME
def sort_data(map_array):
    """Sort array of sunpy maps by time and return indexes used to sort
    """
    times = np.array([obs.date for obs in map_array]) # make array of times
    sorted_i = np.argsort(times)
    sorted_map_array = map_array[sorted_i]

    return sorted_map_array, sorted_i


# GET MEAN CADENCE OF THE OBSERVATION
def get_mean_cadence(map_array):
    """Get the mean cadence of the observation (mean time difference between when two images were taken)."""
    return np.mean(abs(np.diff(get_times(map_array)))).sec


# FIND MAXIMUM AND MINIMUM VALUES OF OBSERVATION
def find_obs_min_and_max(obs):
    """Return the minumum and maximum values in the observations (useful for setting colormap min and max when plotting).
    ** Impose 3 sigma threshold to omit of bad pixels (saturation, etc.) **

    Parameters
    ----------
    obs: np.array of SunPy maps
        observation to find min and max for

    Returns
    -------
    all_min: float
        minimum pixel value in the observation

    all_max: float
        maximum pixel value in the observation
    """
    all_max = obs[0].data[0,0]
    all_min = obs[0].data[0,0]
    
    for elem in obs:
        # 1 sigma cut and then take min, max
        one_std = elem.std()
        one_mean = elem.mean()
        
        cut_data = elem.data[np.where(elem.data < one_mean + 3*one_std)]
        cut_data = cut_data[np.where(cut_data > one_mean - 3*one_std)]
        
        one_max = cut_data.max()
        one_min = cut_data.min()
        
        if one_max > all_max:
            all_max = one_max

        if one_min < all_min:
            all_min = one_min
    
    return all_min, all_max
        


# SAVING DATA ("WHOLE_OBS") AS PICKLE FILE -- SO DON'T HAVE TO KEEP CALLING GET_IRIS_DATA
def save_as_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

# READING IN DATA FROM PICKLE FILE
def read_from_pickle(filename):
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


# PUT IN EARTH TIME
def get_earth_time(obs):
    """Return the observation time in Earth time (if instrument less than 0.05 from Earth, don't change the given time e.g. IRIS observation)
    
    Parameters
    ----------
    obs: SunPy map object
        observation to get earth time for
        
    Returns
    -------
    Earth time of the observation as np.datetime
    """
    time = obs.date
    try:
        dist = obs.fits_header['dsun_obs'] * u.m
    except:
        dist = 1 * u.au # if no sun-instrument value is given set to 1 AU
        
    if abs(1*u.au - dist) < 0.1 * u.au:
        return np.datetime64(time.value) # IRIS
    else:
        dt = (1*u.au - dist) / cst.c
        return np.datetime64((time + dt).value) # SolO -- observers events EARLIER than earth


# CHANGING PLOTTING SETTINGS
def set_obs_plot_settings(obs, setting_name, value):
    for img in obs:
        img.plot_settings[setting_name] = value


############ MATCHING DATA IN TIME ############

# get all the times of a whole observation
def get_times(map_array):
    times = np.array([obs.date for obs in map_array])
    return times


# get all the times of a whole observation
def get_earth_times(map_array):
    times = np.array([get_earth_time(obs) for obs in map_array])
    return times


def find_corresponding_obs(a_whole_obs, wanted_time):
    """Return the observation closest to the given time, where the observation time
    is converted to Earth time.
    
    Parameters
    ----------
    wanted_time: astropy Time object
        the time of interest (Earth time)
            
    Returns
    -------
    "obs" object
        observation closest to the given time, wanted_time
    """
    times = [abs(get_earth_time(obs) - wanted_time) for obs in a_whole_obs]
    closest_i = np.argmin(times)

    return a_whole_obs[closest_i]


def match_obs(whole_obs_to_match, times):
    """Create new np.array of SunPy Maps where each element is a map "whole_obs_to_match" that is closest in time to a element in "times".
    ** No data will be ommited in this matching process -- some maps with be used more than once **
    
    Parameters
    ----------
    whole_obs_to_match: np.array of SunPy maps
        observation to match

    times: list/np.array of astropy Times
        times to match to, must be in earth time
        
    Returns
    -------
    np.array of SunPy maps
        images in whole_obs_to_match repeated or not to match the times given
    """
    matched_array = np.empty(len(times), dtype=type(whole_obs_to_match[0]))

    for i in tqdm(range(len(times))):

        matched_array[i] = find_corresponding_obs(whole_obs_to_match, times[i])

    # multiprocessing doesn't work well -- crashes notebook
    # whole_obs_array = [whole_obs_to_match for i in times]
    # matched_array = p_map(find_corresponding_obs, whole_obs_array, times) # multiprocessing
    # return np.array(matched_array)

    return matched_array


############ DE-ROTATING MAP ############

def correct_diff_rot(one_map, ref):
    """
    https://docs.sunpy.org/en/stable/generated/gallery/differential_rotation/reprojected_map.html

    Parameters
    ----------
    one_map: SunPy map object
        the map to derotate
    
    ref: SunPy map object
        the map to use as a reference for derotating

    
    Returns
    -------
    out_warp: SunPy map object
        "one_map" rotated to "ref"
    """
    in_time = one_map.date
    out_time = ref.date

    out_frame = Helioprojective(observer='earth', obstime=out_time,
                                rsun=one_map.coordinate_frame.rsun)

    out_center = ref.center
    header = sunpy.map.make_fitswcs_header(one_map.data.shape,
                                            out_center,
                                            scale=u.Quantity(one_map.scale))
    out_wcs = WCS(header)

    with propagate_with_solar_surface():
        out_warp = one_map.reproject_to(out_wcs)

    return out_warp


def correct_diff_rot_obs(obs, ref_i=0):

    ref_list = [obs[ref_i] for i in range(len(obs))]
    
    obs_rot = p_map(correct_diff_rot, obs, ref_list)

    obs_rot = sunpy.map.Map(obs_rot, sequence=True)
    
    return obs_rot


############ ALIGNING USING WCS ############

# ALIGN A MAP TO GIVEN WCS
def align_map(map_to_align, map_wcs):
    """Align map to the given map WCS

    Parameters
    ----------
    map_to_align: SunPy map object
        map to reproject
    
    map_wcs: astropy WCS
        map WCS to use to reproject

    Returns
    -------
    Aligned map by using SunPy's reproject_to function (https://docs.sunpy.org/en/stable/generated/api/sunpy.map.GenericMap.html#sunpy.map.GenericMap.reproject_to)
    """
    aligned_map = map_to_align.reproject_to(map_wcs)

    # # preserve original metadata that's lost in the reprojection! -- might be messing up?
    # aligned_map_header = aligned

    # # map units in 'BUNIT'
    # for key in map_to_align.fits_header.keys():
    #     if key not in aligned_map_header and key != 'COMMENT' and key != 'HISTORY':
    #         # for every header entry that isn't in the aligned map's header, set it to the original map's value
    #         aligned_map_header[key] = map_to_align.fits_header[key]

    # aligned_map = sunpy.map.Map(aligned_map.data, aligned_map_header)

    return aligned_map


# ALIGN OBSERVATIONS TO A REFERENCE OBSERVATION
def align_obs_to_reference(whole_obs_to_align, ref_obs):
    """Align a whole observation to a reference map's coordinate system.
    ** using multiprocessing so aligning will run faster! **

    Parameters
    ----------
    whole_obs_to_align: np.array of SunPy maps

    ref_obs: SunPy map
        will reproject observations to this map's WCS

    Returns
    -------
    np.array of SunPy maps
        whole_obs_to_align but reprojected to ref_obs's WCS
    """
    ref_obs_list = [ref_obs.wcs for i in whole_obs_to_align] # make array of the same length

    aligned_whole_obs = p_map(align_map, whole_obs_to_align, ref_obs_list) # multiprocessing!

    return np.array(aligned_whole_obs)


# # MATCH TWO OBSERVATIONS IN TIME AND ALIGN THEM SPATIALLY
# def match_and_align_obs(whole_obs1, whole_obs2):
#     """Match the observations in time and align the matched observations spatially.

#     Parameters
#     ----------
#     whole_obs1: "whole_obs" object
#         observation to match and align (whole_obs2 will be reprojected to this WCS)

#     whole_obs2: "whole_obs" object
#         observation to match and align (will be reprojected to whole_obs1 WCS)

#     Returns
#     -------
#     matched_obs1: "whole_obs" object
#         matched observations from whole_obs1

#     aligned_whole_obs1: "whole_obs" object
#         matched and aligned observations from whole_obs1

#     aligned_whole_obs2: "whole_obs" object
#         matched and aligned observations from whole_obs2

#     matched_obs2: "whole_obs" object
#         matched observations from whole_obs2 (also returning this because aligned_whole_obs2 has inaccurate metadata -- e.g. time)
#     """

#     # first match the observations in time
#     matched_obs1, matched_obs2 = whole_obs1.match_obs(whole_obs2)

#     # align the observations
#     aligned_whole_obs1, aligned_whole_obs2 = align_obs(matched_obs1, matched_obs2)

#     return [matched_obs1, aligned_whole_obs1], [matched_obs2, aligned_whole_obs2]


############ CROSS CORRELATION / MANUAL ALIGNMENT ############

# CROSS CORRELATE TO FIND THE X AND Y SHIFTS TO ALIGN TWO IMAGES
def cross_correlate(img1, img2, upsample_factor=100): # FOR CROSS CORRELATING EUI IMAGES WITH ITSELF
    """Return the found shift values when cross correlating "img1" and "img2"
    ** Sub-pixel cross correlation  -- faster than np.scipy.signal.correlate (https://scikit-image.org/docs/stable/api/skimage.registration.html#skimage.registration.phase_cross_correlation) **
    
    Parameters
    ----------
    img1: reference image

    img2: moving image 

    Returns
    -------
    shift: 
    """
    img1[np.isnan(img1)] = 0; img2[np.isnan(img2)] = 0 # set NAN values to 0

    # shift = phase_cross_correlation(img1, # reference image
    #                                 img2, # moving image
    #                                 upsample_factor=upsample_factor,
    #                                 reference_mask=~np.isnan(img1),
    #                                 moving_mask=~np.isnan(img2))

    shift, _, _ = phase_cross_correlation(img1, # reference image
                                            img2, # moving image
                                            upsample_factor=upsample_factor)

    return shift

# CROSS CORRELATE TO FIND THE X AND Y SHIFTS TO ALIGN TWO IMAGES
def cross_correlate_mask(img1, img2, upsample_factor=100): # FOR CROSS CORRELATING IRIS 1400 AND AIA 1600
    """Return the found shift values when cross correlating "img1" and "img2"
    ** Sub-pixel cross correlation  -- faster than np.scipy.signal.correlate (https://scikit-image.org/docs/stable/api/skimage.registration.html#skimage.registration.phase_cross_correlation) **
    
    Parameters
    ----------
    img1: reference image

    img2: moving image 

    Returns
    -------
    shift: 
    """
    shift = phase_cross_correlation(img1, # reference image
                                    img2, # moving image
                                    upsample_factor=upsample_factor,
                                    reference_mask=~np.isnan(img1),
                                    moving_mask=~np.isnan(img2))
    return shift


# # CROSS CORRELATE TO FIND THE X AND Y SHIFTS TO ALIGN AN OBSERVATION TO ITS CENTRAL OBSERVATION
# def cross_correlate_with_an_image(whole_obs_to_shift, img_index, xstart=0, xend=-1, ystart=0, yend=-1):
#     """Return arrays of offset values when correlating each image in an observation to its middle image.
#     ** using multiprocessing so cross-correlation will run faster! **

#     Parameters
#     ----------
#     whole_obs_to_shift: np.array of SunPy maps
#         observation of interest

#     xstart, xend, ystart, yend: int
#         to specify subset of the image to use for cross correlation (runs quicker the less data it has to consider)

#     Returns
#     -------
#     xshifts, yshifts: list of integers
#         x/y shifts to apply
#     """
#     img_list = [obs.data[ystart:yend, xstart:xend] for obs in whole_obs_to_shift]
#     ref_imgs = [img_list[img_index] for i in img_list] # make list so will run in multiprocessing format

#     shifts = p_map(cross_correlate, img_list, ref_imgs) # multiprocessing!

#     shifted_obs = shift_obs(whole_obs_to_shift, shifts)
    
#     # xshifts = np.empty(len(img_list)); yshifts = np.empty(len(img_list))
#     # for i in range(len(img_list)):
#     #     xshifts[i] = int(shifts[i][0])
#     #     yshifts[i] = int(shifts[i][1])
        
#     return shifts, shifted_obs


# CROSS CORRELATE TO FIND THE X AND Y SHIFTS TO ALIGN TWO WHOLE OBSERVATIONS
def cross_correlate_all(whole_obs1, whole_obs2, xstart=0, xend=-1, ystart=0, yend=-1):
    """Find offset values when cross correlating each aligned image in two observations 
    ** whole_obs1 and whole_obs2 are matched and aligned -- the same size! **
    ** using multiprocessing so cross-correlation will run faster! **
    
    Parameters
    ----------
    whole_obs1, whole_obs2: np.array of SunPy maps
        the two observations to cross correlate
        whole_obs1 is the observation you want to shift!

    xstart, xend, ystart, yend = int
        to specify subset of the image to use for cross correlation (runs quicker the less data it has to consider)

    Returns
    -------
    xstart, xend, ystart, yend = int
        to specify subset of the image to use for cross correlation (runs quicker the less data it has to consider)
    """
    # xshifts = np.empty(len(whole_obs1)); yshifts = np.empty(len(whole_obs1))

    img1_list = [obs.data[ystart:yend, xstart:xend] for obs in whole_obs1] # take image subset if specified
    img2_list = [obs.data[ystart:yend, xstart:xend] for obs in whole_obs2]

    shifts = p_map(cross_correlate, img2_list, img1_list) # multiprocessing!
    
    # for i in range(len(img1_list)):
    #     xshifts[i] = int(shifts[i][0])
    #     yshifts[i] = int(shifts[i][1])

    return shifts


# SMOOTH THE SHIFTS FROM CROSS CORRELATING USING NP.CONVOLVE
def smooth_shifts(shifts, kernel_size=20):
    """# https://danielmuellerkomorowska.com/2020/06/02/smoothing-data-by-rolling-average-with-numpy/
    """
    y = []; x = []
    for i in shifts:
        y.append(i[0]); x.append(i[1])

    kernel = np.ones(kernel_size) / kernel_size
    y_convolved = np.convolve(y, kernel, mode='same')
    x_convolved = np.convolve(x, kernel, mode='same')

    y_convolved[:kernel_size] = y[:kernel_size]
    y_convolved[-kernel_size:] = y[-kernel_size:]
    x_convolved[:kernel_size] = x[:kernel_size]
    x_convolved[-kernel_size:] = x[-kernel_size:]

    shifts_smoothed = []

    for i in range(len(y_convolved)):
        shifts_smoothed.append(np.array([y_convolved[i], x_convolved[i]]))

    return shifts_smoothed




############ SHIFTING IMAGES -- APPLYING MANUAL ALIGNMENT ############

# APPLYING X AND Y SHIFTS AND RETURNING NEW SUNPY MAP
def apply_shift(img, shift):
    """Perform sub-pixel image shift using fast fourier transforms (using scipy.ndimage's fourier_shift)
    
    Parameters
    ----------
    img: SunPy Map
        map to shift
        
    shift: lst, size 2 (output of cross_correlate)
        shift[0] is shift to apply in y; shift[1] is shift to apply in x

    Returns
    -------
    shift_map: SunPy Map
        "img" shifted using values specified in "shift". Shifted bounds filled in with zeroes.
    """

    shift_img = fourier_shift(np.fft.fftn(img.data), shift)
    shift_img = np.fft.ifftn(shift_img).real # only keep real part

    # fill in parts of the shifted array with zeroes -- round up to integer
    y, x = shift
    if y > 0:
        shift_img[:int(y+1), :] = 0
    else:
        shift_img[int(y-1):, :] = 0

    if x > 0:
        shift_img[:, :int(x+1)] = 0
    else:
        shift_img[:, int(x-1):] = 0

    # recreate SunPy map
    shift_map = sunpy.map.Map((shift_img, img.meta))

    return shift_map

def apply_shift_nan(img, shift):
    """same as apply_shift but accouting for nan values differently -- use for iris obs"""
    
    data = img.data
    
    data[np.isnan(data)] = 0
    
    shift_img = fourier_shift(np.fft.fftn(data), shift)
    shift_img = np.fft.ifftn(shift_img).real # only keep real part

    # fill in parts of the shifted array with zeroes -- round up to integer
    y, x = shift
    if y > 0:
        shift_img[:int(y+1), :] = np.nan
    else:
        shift_img[int(y-1):, :] = np.nan

    if x > 0:
        shift_img[:, :int(x+1)] = np.nan
    else:
        shift_img[:, int(x-1):] = np.nan

    # recreate SunPy map
    shift_map = sunpy.map.Map((shift_img, img.meta))

    return shift_map


# APPLY THE SAME X AND Y SHIFT TO ALL IMAGES IN AN OBSERVATION
def shift_obs(whole_obs_to_shift, shifts):
    """Apply shift factor to all images in the whole observation.

    Parameters
    ----------
    whole_obs_to_shift: np.array of SunPy maps
        the observation that you want to shift its images

    shifts: lst (output of cross_correlate_all)
        shift[:][0] are the shifts to apply in y; shift[:][1] are the shifts to apply in x

    Returns
    -------
    shifted_data_array: np.array of SunPy maps
        "whole_obs_to_shift" but with the specified x_shift/y_shift applied to the image data
    """
    # shifted_data_array = np.empty(len(whole_obs_to_shift), dtype=type(whole_obs_to_shift[0])) # make empty array of SunPy maps

    shifted_data = p_map(apply_shift, whole_obs_to_shift, shifts)

    # if len(shift) < 2: # if given x and y shifts are integers

    #     for i, one_map in enumerate(tqdm(whole_obs_to_shift)):

    #             shifted_map = apply_shift(one_map, shift) # shift each image by the same x and y
    #             shifted_data_array[i] = shifted_map

    # else: # if given x and y shifts are arrays

    #     for i, one_map in enumerate(tqdm(whole_obs_to_shift)):

    #         shifted_map = apply_shift(one_map, shift) # shift each image by unique x and y
    #         shifted_data_array[i] = shifted_map

    return shifted_data  # array of sunpy maps



############ ZOOMING INTO A REGION ############

def create_one_submap(one_map, xlims, ylims):
    """Return subregion of "one_map" specified by "xlims" and "ylims" (using SunPy submap() function)

    Parameters
    ----------
    one_map: SunPy Map
        map to get subregion of

    xlims: list, size 2
        xlims[0] is lower bound and xlims[1] is upper bound

    ylims: list, size 2
        ylims[0] is lower bound and ylims[1] is upper bound

    Returns
    -------
    SunPy Map
        subsection of "one_map"
    """
    # convert pixel position to Skycoord
    bottom_left = one_map.pixel_to_world(xlims[0]*u.pix, ylims[0]*u.pix)
    top_right = one_map.pixel_to_world(xlims[1]*u.pix, ylims[1]*u.pix)

    return one_map.submap(bottom_left=bottom_left, top_right=top_right)


def create_obs_submaps(obs, xlims, ylims):
    """Return subregion of each map in "obs" specified by "xlims" and "ylims" (see create_one_submap)
    
    Parameters
    ----------
    obs: np.array of SunPy Maps
        observation to get subregion of 

    xlims: list, size 2
        xlims[0] is lower bound and xlims[1] is upper bound

    ylims: list, size 2
        ylims[0] is lower bound and ylims[1] is upper bound
    
    Returns
    -------
    submaps: np.array of SunPy Maps
        "obs" but each map is a subsection
    """
    submaps = np.empty(len(obs), dtype=type(obs[0])) # make empty array of SunPy maps
    
    for i, one_map in enumerate(tqdm(obs)):
        
        submap = create_one_submap(one_map, xlims, ylims)
        
        submaps[i] = submap

    # set plot settings
    set_obs_plot_settings(submaps, 'cmap', obs[0].plot_settings['cmap'])
    set_obs_plot_settings(submaps, 'norm', obs[0].plot_settings['norm'])
        
    return submaps


###### CUTTING OBSERVATIONS SO THEY'RE THE SAME LENGTH ######
def obs_overlap_times(obs1, obs2):
    """Find the start and end of the overlap time between two observations, in terms of Earth time.

    Parameters
    ----------
    other_obs: "whole_obs" object
        the other observation to compare to

    Returns
    -------
    latest_start_time: astropy Time object
        the earliest time the two observations have in common

    earliest_end_time: astropy Time object
        the lastest time the two observations have in common
    """
    times1 = np.sort([get_earth_time(one_obs) for one_obs in obs1])
    start_time1 = times1[0]
    end_time1 = times1[-1]

    times2 = np.sort([get_earth_time(one_obs) for one_obs in obs2])
    start_time2 = times2[0]
    end_time2 = times2[-1]

    # find latest start time
    latest_start_time = start_time1
    if start_time2 > start_time1:
        latest_start_time = start_time2

    # find earliest end time
    earliest_end_time = end_time1
    if end_time2 < end_time1:
        earliest_end_time = end_time2
    
    return latest_start_time, earliest_end_time


def find_corresponding_obs_i(obs, wanted_time):
    """Return the observation closest to the given time, where the observation time
    is converted to Earth time.
    
    Parameters
    ----------
    wanted_time: astropy Time object
        the time of interest (Earth time)
            
    Returns
    -------
    "obs" object
        observation closest to the given time, wanted_time
    """
    times = [abs(get_earth_time(one_obs) - wanted_time) for one_obs in obs]
    closest_i = np.argmin(times)

    return closest_i


def cut_obs(obs, start_time, end_time):
    """Return observation cut to the given times.

    Parameters
    ----------
    start: astropy Time object
        the first time you want to include
    
    end: astropy Time object
        the last time you want to include
    
    Returns
    -------
    cut_obs: "whole_obs" object
        the given observation cut to the start and end times
    """
    # get closest time to start
    start_i = find_corresponding_obs_i(obs, start_time)

    # get closest time to end
    end_i = find_corresponding_obs_i(obs, end_time)

    cut_data_array = obs[start_i:end_i]

    return cut_data_array
