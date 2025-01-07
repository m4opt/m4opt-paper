import warnings

warnings.filterwarnings("ignore", "Wswiglal-redir-stdio")

from astropy import units as u
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from m4opt.fov import footprint
from m4opt.missions import uvex
import ligo.skymap.plot
from tqdm.auto import tqdm
from plots import customize_style

customize_style()
plt.rcParams["figure.figsize"][1] = plt.rcParams["figure.figsize"][0]

fig = plt.figure(dpi=300)
ax = fig.add_subplot(projection="astro globe")
for coord in ax.coords:
    coord.set_ticks_visible(False)
    coord.set_ticklabel_visible(False)
fig.tight_layout()

frames = np.arange(0, 90, 5)
artists_to_delete = []
with tqdm(total=len(frames) + 3, desc="drawing", unit="frame") as progress:

    def func(rotation):
        result = []
        while artists_to_delete:
            artist = artists_to_delete.pop()
            result.append(artist)
            artist.remove()
        for region in footprint(uvex.fov, uvex.skygrid, rotation * u.deg):
            artist = region.to_pixel(ax.wcs).as_artist(linewidth=0.25)
            artists_to_delete.append(artist)
            result.append(artist)
            ax.add_patch(artist)
        progress.update()
        return result

    func(45)
    fig.savefig("figures/skygrid.png")

    with tqdm(total=len(frames), desc="saving", unit="frame") as saving_progress:
        FuncAnimation(
            fig=fig,
            func=func,
            frames=frames,
            blit=True,
            repeat=True,
            interval=50,
        ).save(
            "figures/skygrid.gif",
            progress_callback=lambda i, _: saving_progress.update(),
        )
