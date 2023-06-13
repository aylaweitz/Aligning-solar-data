# IMPORT STATEMENTS

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import pickle
import scipy
import datetime

import astropy.units as u
import astropy.constants as cst
import sunpy.map
import sunpy.sun.constants
import sunpy_soar
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from reproject import reproject_interp
from reproject.mosaicking import reproject_and_coadd
from sunpy.coordinates import HeliographicCarrington, HeliographicStonyhurst, Helioprojective
from sunpy.net import Fido
import sunpy.net.attrs as a
import pandas as pd

from astropy.io import fits
from tqdm import tqdm
from matplotlib.animation import FFMpegWriter

import multiprocessing as mp # for parallel processing!
from p_tqdm import p_map, p_umap, p_imap, p_uimap # https://github.com/swansonk14/p_tqdm -- "p_tqdm is a wrapper around pathos.multiprocessing and tqdm"

from skimage.registration import phase_cross_correlation
from skimage.registration._phase_cross_correlation import _upsampled_dft
from scipy.ndimage import fourier_shift
from scipy.interpolate import UnivariateSpline
import skimage.filters

import os
from matplotlib import colors
from matplotlib import patches

from astropy.visualization import ImageNormalize, SqrtStretch
import matplotlib.animation as animation

from sunpy.physics.differential_rotation import diff_rot, solar_rotate_coordinate
from sunpy.coordinates import Helioprojective, propagate_with_solar_surface

from skimage.feature import blob_dog

###

# for some AIA data, "arcsecs" instead of "arcsec" is written an astropy doesn't recognize it
arcsecs = u.def_unit('arcsecs', 1 *  u.arcsec)
u.add_enabled_units(arcsecs)