from plots import customize_style
import ligo.skymap.plot
from matplotlib import pyplot as plt
import numpy as np
from astropy_healpix import HEALPix
from astropy.coordinates import Galactic, EarthLocation
from astropy.time import Time
import synphot
from m4opt.missions import uvex as mission
from m4opt.models import observing, DustExtinction
from astropy import units as u

customize_style()

hpx = HEALPix(nside=512, frame=Galactic())

with observing(
    observer_location=EarthLocation(0 * u.m, 0 * u.m, 0 * u.m),
    target_coord=hpx.healpix_to_skycoord(np.arange(hpx.npix)),
    obstime=Time("2024-01-01"),
):
    limmag = mission.detector.get_limmag(
        5,
        900 * u.s,
        synphot.SourceSpectrum(synphot.ConstFlux1D, amplitude=0 * u.ABmag)
        * synphot.SpectralElement(DustExtinction()),
        "NUV",
    ).to_value(u.mag)
limmag[np.isnan(limmag)] = -np.inf

fig = plt.figure(tight_layout=True)
ax = fig.add_subplot(projection="geo hours aitoff")
ax.grid()
plt.colorbar(ax.contourf_hpx(limmag, cmap='plasma_r', levels=[20, 21, 22, 23, 24, 25]))
fig.savefig("figures/exptime-position.pdf")
