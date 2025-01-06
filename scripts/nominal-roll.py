from astropy.coordinates import (
    EarthLocation,
    GeocentricMeanEcliptic,
    SkyCoord,
    get_body,
)
from astropy.time import Time
from astropy import units as u
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from m4opt.dynamics import nominal_roll
import numpy as np
from plots import customize_style

customize_style()
plt.rcParams["figure.figsize"][1] = 3.5

# Place the observer at the center of the Earth.
# Note that for observers in Earth orbit, the impact of the orbital phase
# is negligible because the orbit is much smaller than the Earth-Sun distance.
observer_location = EarthLocation.from_geocentric(0, 0, 0, unit=u.m)
obstime = Time("2024-01-1") + np.linspace(0, 1, 1000) * u.year
sun_lon = np.unwrap(
    get_body("sun", obstime).transform_to(GeocentricMeanEcliptic).lon,
    period=360 * u.deg,
)

fig, ax = plt.subplots(
    gridspec_kw=dict(bottom=0.2, left=0.2, right=0.75, top=0.975),
    subplot_kw=dict(aspect=1),
)
for lat in np.arange(0, 100, 10) * u.deg:
    target_coord = SkyCoord(0 * u.deg, lat, frame=GeocentricMeanEcliptic)
    roll = nominal_roll(observer_location, target_coord, obstime)
    ax.plot(
        sun_lon,
        360 * u.deg + np.unwrap(roll, period=360 * u.deg),
        label=lat.to_string(format="latex"),
    )

ax.set_xlim(sun_lon.min().to_value(u.deg), sun_lon.max().to_value(u.deg))
ax.xaxis.set_major_locator(MultipleLocator(90))
ax.xaxis.set_major_formatter(
    lambda x, _: {
        0: "March equinox",
        90: "June solstice",
        180: "Sept. equinox",
        270: "Dec. solstice",
    }[x % 360]
)

ax.set_ylim(-15, 445)
ax.yaxis.set_major_locator(MultipleLocator(90))
ax.yaxis.set_major_formatter(lambda x, _: rf"{x:g}°")
ax.set_ylabel("Nominal roll angle (°)")

fig.legend(title="Ecliptic\nlatitude", loc="outside upper right", frameon=False)

ax.spines["left"].set_position(("data", sun_lon.min().to_value(u.deg)))
ax.spines["bottom"].set_position(("data", 0))
ax.spines["top"].set_color("none")
ax.spines["right"].set_color("none")
# ax.plot(ax.get_xlim()[0], ax.spines["bottom"].get_position()[1], "<k", clip_on=False)
ax.plot(ax.get_xlim()[1], ax.spines["bottom"].get_position()[1], ">k", clip_on=False)
ax.plot(ax.spines["left"].get_position()[1], ax.get_ylim()[0], "vk", clip_on=False)
ax.plot(ax.spines["left"].get_position()[1], ax.get_ylim()[1], "^k", clip_on=False)
ax.grid()

plt.setp(
    ax.xaxis.get_ticklabels(), ha="left", va="top", rotation_mode="anchor", rotation=-30
)

fig.savefig("figures/nominal-roll.pdf")
