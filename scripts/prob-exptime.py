from pathlib import Path

from astropy.table import QTable
from detection_probability import get_detection_probability_unknown_position
from ligo.skymap.io import read_sky_map

base_path = Path("data")
run = "O5"
event_id = 800
skymap_moc = read_sky_map(base_path / run / f"{event_id}.fits", moc=True)
plan_args = QTable.read(base_path / run / f"{event_id}.ecsv").meta["args"]


def process(path):
    return get_detection_probability_unknown_position(
        QTable.read(path), skymap_moc, plan_args
    )


if __name__ == "__main__":
    import numpy as np
    from ligo.skymap.util.progress import progress_map
    from matplotlib import pyplot as plt
    from plots import customize_style

    customize_style()

    exptimes = np.arange(300, 3700, 100)

    variable_exptime_prob, *fixed_exptime_probs = progress_map(
        process,
        [
            base_path / run / f"{event_id}.ecsv",
            *(
                base_path / run / f"{event_id}-exptime-{exptime}s.ecsv"
                for exptime in exptimes
            ),
        ],
        jobs=None,
    )

    adaptive_color = "darkmagenta"
    fixed_color = "tab:blue"

    fig, ax = plt.subplots(tight_layout=True)
    ax.set_xlim(0, 3.75)
    ax.set_ylim(0.2, 0.8)
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
        0.5,
        "Fixed exposure time",
        ha="center",
        va="top",
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
