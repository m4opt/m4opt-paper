import ligo.skymap.plot  # noqa: F401
import numpy as np
import regions
from astropy import units as u
from astropy.coordinates import ICRS, SkyCoord
from astropy_healpix import HEALPix
from m4opt.fov import footprint_healpix
from m4opt.missions import uvex
from matplotlib import pyplot as plt
from plots import customize_style

customize_style()
plt.rcParams["figure.figsize"][1] = plt.rcParams["figure.figsize"][0]

center = SkyCoord(0 * u.deg, 0 * u.deg)
hpx = HEALPix(nside=128, frame=ICRS())

fig = plt.figure(tight_layout=True)
ax = fig.add_subplot(projection="astro zoom", center=center, radius=2.5 * u.deg)
ax.coords.frame.set_color("none")
transform = ax.get_transform("world")


def plot_boundaries(ipix, **kwargs):
    lons, lats = hpx.boundaries_lonlat(ipix, 1)
    coords = np.moveaxis([lons.to_value(u.deg), lats.to_value(u.deg)], 0, -1)
    for coord in coords:
        ax.add_patch(plt.Polygon(coord, transform=transform, **kwargs))


plot_limit_ipix = footprint_healpix(
    hpx,
    regions.PolygonSkyRegion(SkyCoord(*ax.wcs.calc_footprint().T, unit=u.deg)),
    center,
)
plot_boundaries(
    plot_limit_ipix,
    facecolor="none",
    edgecolor=plt.rcParams["grid.color"],
    linewidth=plt.rcParams["grid.linewidth"],
)

fov_boundaries = footprint_healpix(hpx, uvex.fov, center)
plot_boundaries(
    fov_boundaries, edgecolor="black", linewidth=plt.rcParams["lines.linewidth"]
)

ax.add_artist(
    uvex.fov.to_pixel(ax.wcs).as_artist(
        edgecolor="black", linewidth=plt.rcParams["axes.linewidth"]
    )
)

for coord in ax.coords:
    coord.set_axislabel(None)
    coord.set_ticks_visible(False)
    coord.set_ticklabel_visible(False)
fig.savefig("figures/fov.pdf")
