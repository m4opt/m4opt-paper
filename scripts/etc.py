from astropy import units as u
from astropy.coordinates import EarthLocation, ICRS
from astropy_healpix import HEALPix
from astropy.time import Time
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from m4opt.missions import uvex
from m4opt.synphot import observing
import numpy as np
from synphot import ConstFlux1D, SourceSpectrum

from plots import customize_style
customize_style()

dwell = u.def_unit("dwell", 900 * u.s)
exptime = np.arange(1, 11) * dwell
obstime = Time("2024-01-01") + np.linspace(0, 1) * u.year
hpx = HEALPix(128, frame=ICRS())
target_coords = hpx.healpix_to_skycoord(np.arange(hpx.npix))
observer_location = EarthLocation(0 * u.m, 0 * u.m, 0 * u.m)

limmags = []
for filt in uvex.detector.bandpasses.keys():
    with observing(
        observer_location,
        target_coords[np.newaxis, :, np.newaxis],
        obstime[np.newaxis, np.newaxis, :],
    ):
        limmags.append(
            uvex.detector.get_limmag(
                5 * np.sqrt(dwell / exptime[:, np.newaxis, np.newaxis]),
                1 * dwell,
                SourceSpectrum(ConstFlux1D, amplitude=0 * u.ABmag),
                filt,
            ).to_value(u.mag)
        )
median_limmags = np.median(limmags, axis=[2, 3])

colors = ['darkmagenta', 'tab:blue']
fig, ax = plt.subplots(tight_layout=True)
ax.set_xlim(0, 10.5)
ax.set_ylim(24.4, 26.5)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.grid()
ax.invert_yaxis()
for filt, limmag, color in zip(uvex.detector.bandpasses.keys(), median_limmags, colors):
    ax.plot(exptime, limmag, "-o", label=filt, color=color, clip_on=False)
    ax.annotate(filt, (10, limmag[-1]), (7.5, 0), textcoords='offset points', ha='left', va='center', fontsize=plt.rcParams['legend.fontsize'], clip_on=False)
ax.set_xlabel("Number of stacked 900 s dwells")
ax.set_ylabel(r"5-$\sigma$ limiting magnitude (AB)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.plot(ax.get_xlim()[1], ax.get_ylim()[0], ">k", clip_on=False)

plt.savefig("figures/etc.pdf")
