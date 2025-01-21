from plots import customize_style
from matplotlib import pyplot as plt
import numpy as np
from astropy.table import QTable
from ligo.skymap.io import read_sky_map
from detection_probability import get_detection_probability_unknown_position
from pathlib import Path
from tqdm.auto import tqdm

customize_style()

base_path = Path("runs_SNR-10")
run = "O5HLVK"
event_id = 800
# run = "O6HLVK"
# event_id = 6427
exptimes = np.arange(300, 3700, 100)
variable_exptime_plan = QTable.read(
    base_path / run / "farah" / "allsky" / f"{event_id}.ecsv"
)
fixed_exptime_plans = [
    QTable.read(
        base_path / run / "farah" / "allsky" / f"{event_id}-exptime-{exptime}s.ecsv"
    )
    for exptime in tqdm(exptimes)
]
skymap_moc = read_sky_map(
    base_path / run / "farah" / "allsky" / f"{event_id}.fits", moc=True
)

variable_exptime_prob, *fixed_exptime_probs = [
    get_detection_probability_unknown_position(
        plan, skymap_moc, variable_exptime_plan.meta["args"]
    )
    for plan in tqdm([variable_exptime_plan, *fixed_exptime_plans])
]

adaptive_color = 'darkmagenta'
fixed_color = 'tab:blue'

fig, ax = plt.subplots(tight_layout=True)
ax.set_xlim(0, 3.75)
ax.set_ylim(0.6, 1)
ax.axhline(variable_exptime_prob, linestyle="--", color=adaptive_color)
ax.text(
    np.mean(ax.get_xlim()),
    variable_exptime_prob,
    "Variable exposure time",
    ha="center",
    va="bottom",
    color=adaptive_color,
    fontsize=plt.rcParams["axes.labelsize"],
)
ax.text(
    np.mean(ax.get_xlim()),
    0.75,
    "Fixed exposure time",
    ha="center",
    color=fixed_color,
    fontsize=plt.rcParams["axes.labelsize"],
)
ax.plot(exptimes / 1000, fixed_exptime_probs, color=fixed_color)
ax.yaxis.set_major_formatter(lambda y, _: f"{100 * y:g}%")
ax.set_xlabel("Per-field exposure time (ks)")
ax.set_ylabel("Detection probability")
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.plot(ax.get_xlim()[1], ax.get_ylim()[0], ">k", clip_on=False)
fig.savefig("figures/prob-exptime.pdf")
