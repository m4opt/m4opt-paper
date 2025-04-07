import numpy as np
import synphot
from astropy import units as u
from astropy.coordinates import ICRS, EarthLocation
from astropy.table import QTable, Table
from astropy.utils.masked import Masked
from astropy_healpix import HEALPix
from ligo.skymap.bayestar import rasterize
from ligo.skymap.distance import parameters_to_marginal_moments, parameters_to_moments
from ligo.skymap.io import read_sky_map
from m4opt import missions
from m4opt.fov import footprint_healpix
from m4opt.synphot import DustExtinction, observing
from m4opt.synphot._math import countrate
from scipy import stats

plan = QTable.read("data/O5/4678.ecsv")
plan_args = plan.meta["args"]
hpx = HEALPix(nside=plan_args["nside"], order="nested", frame=ICRS())
mission = getattr(missions, plan_args["mission"])
snr = plan_args["snr"]
bandpass = plan_args["bandpass"]

skymap_moc = read_sky_map(plan_args["skymap"], moc=True)
skymap = rasterize(skymap_moc, order=hpx.level)

observations = plan[plan["action"] == "observe"].filled()
footprints = footprint_healpix(
    hpx, mission.fov, observations["target_coord"], observations["roll"]
)

# Evaluate the limiting magnitude for each observation, for each pixel.
# Note that because each field may contain a different number of pixels,
# we can't use Numpy array broadcasting. Instead, we repeat the entries
# from the observer_location and time columns an appropriate number of
# times.
#
# FIXME: This is a more complicated than it should be because neither
# `astropy.coordinates.EarthLocation` nor `astropy.time.Time` support
# `np.full` or `np.concatenate`.
observation_midtimes = observations["start_time"] + 0.5 * observations["duration"]
flat_spectrum = synphot.SourceSpectrum(synphot.ConstFlux1D, amplitude=0 * u.ABmag)
dusty_flat_spectrum = flat_spectrum * DustExtinction()
bandpass_spectrum = mission.detector.bandpasses[plan_args["bandpass"]]
with observing(
    observer_location=EarthLocation.from_geocentric(
        *(
            np.concatenate(
                [
                    np.tile(value, (len(footprint), 1))
                    for value, footprint in zip(
                        np.column_stack(
                            [
                                coord.value
                                for coord in observations[
                                    "observer_location"
                                ].geocentric
                            ]
                        ),
                        footprints,
                    )
                ]
            ).T
            * observations["observer_location"].geocentric[0].unit
        )
    ),
    target_coord=hpx.healpix_to_skycoord(np.concatenate(footprints)),
    obstime=observation_midtimes[0]
    + np.concatenate(
        [
            np.full(len(footprint), value)
            for value, footprint in zip(
                (observation_midtimes - observation_midtimes[0]).to_value(u.s),
                footprints,
            )
        ]
    )
    * u.s,
):
    limmag_no_dust = mission.detector.get_limmag(
        snr,
        np.concatenate(
            [
                np.full(len(footprint), value)
                for value, footprint in zip(observations["duration"].value, footprints)
            ]
        )
        * observations["duration"].unit,
        flat_spectrum,
        bandpass,
    ).to_value(u.mag)
    limmag = mission.detector.get_limmag(
        snr,
        np.concatenate(
            [
                np.full(len(footprint), value)
                for value, footprint in zip(observations["duration"].value, footprints)
            ]
        )
        * observations["duration"].unit,
        dusty_flat_spectrum,
        bandpass,
    )
    dust_extinction = (
        countrate(DustExtinction() * flat_spectrum, bandpass_spectrum)
        / countrate(flat_spectrum, bandpass_spectrum)
    ).to_value(u.mag(u.dimensionless_unscaled))
    background = (
        countrate(mission.detector.background, bandpass_spectrum)
        / countrate(flat_spectrum, bandpass_spectrum)
    ).to_value(u.mag(u.dimensionless_unscaled))


distmean, diststd, _ = parameters_to_moments(skymap["DISTMU"], skymap["DISTSIGMA"])
distmean = distmean[np.concatenate(footprints)]
diststd = diststd[np.concatenate(footprints)]
sigma2_log = np.log1p(np.square(diststd / distmean))
logdistsigma = np.sqrt(sigma2_log)
logdistmu = np.log(distmean) - 0.5 * sigma2_log

absmagmu = plan_args["absmag_mean"]
absmagsigma = plan_args["absmag_stdev"]
a = 5 / np.log(10)
appmagmu = absmagmu + a * logdistmu + 25
appmagsigma = np.sqrt(np.square(absmagsigma) + np.square(a * logdistsigma))

detection_prob_integrand = skymap["PROB"][np.concatenate(footprints)] * stats.norm(
    loc=appmagmu, scale=appmagsigma
).cdf(limmag)

i = np.concatenate(
    [np.full(len(footprint), i) for i, footprint in enumerate(footprints)]
)
table = (
    Table(
        {
            "i": i,
            "limmag": limmag_no_dust,
            "dust": dust_extinction,
            "background": background,
        }
    )
    .group_by("i")
    .groups.aggregate(np.median)
)
table.sort("i")
table["prob"] = [skymap["PROB"][footprint].sum() for footprint in footprints]
table["dist"] = [
    parameters_to_marginal_moments(
        skymap[footprint]["PROB"] / skymap[footprint]["PROB"].sum(),
        skymap[footprint]["DISTMU"],
        skymap[footprint]["DISTSIGMA"],
    )[0]
    for footprint in footprints
]

table2 = (
    Table({"i": i, "detection_prob": detection_prob_integrand})
    .group_by("i")
    .groups.aggregate(np.sum)
)
table2.sort("i")
table["detection_prob"] = table2["detection_prob"]

for key in ["limmag", "dust", "background", "prob", "dist", "detection_prob"]:
    plan[key] = Masked(
        np.asarray(table[key]).repeat(2),
        mask=np.tile(np.arange(2, dtype=bool), len(observations)),
    )[:-1]

plan["start_time"].precision = 0
with open("tables/example.tex", "w") as f:
    for i, row in enumerate(plan):
        print(
            str(row["start_time"]).split()[1],
            int(np.rint(row["duration"].to_value(u.s))),
            row["action"],
            "---"
            if row["observer_location"].mask
            else int(np.rint(row["observer_location"].geocentric[0].to_value(u.Mm))),
            "---"
            if row["observer_location"].mask
            else int(np.rint(row["observer_location"].geocentric[1].to_value(u.Mm))),
            "---"
            if row["observer_location"].mask
            else int(np.rint(row["observer_location"].geocentric[2].to_value(u.Mm))),
            "---"
            if row["target_coord"].mask
            else np.format_float_positional(
                row["target_coord"].ra.deg,
                fractional=True,
                trim="k",
                precision=4,
                min_digits=4,
            ),
            "---"
            if row["target_coord"].mask
            else np.format_float_positional(
                row["target_coord"].dec.deg,
                fractional=True,
                trim="k",
                precision=4,
                min_digits=4,
                sign=True,
            ),
            "---" if row["roll"].mask else int(np.rint(row["roll"].to_value(u.deg))),
            "---"
            if row["prob"].mask
            else np.format_float_positional(
                row["prob"],
                fractional=True,
                trim="k",
                precision=2,
                min_digits=2,
            ),
            "---" if row["dist"].mask else int(np.rint(row["dist"])),
            "---"
            if row["limmag"].mask
            else np.format_float_positional(
                row["limmag"],
                fractional=True,
                trim="k",
                precision=2,
                min_digits=2,
            ),
            "---"
            if row["dust"].mask
            else np.format_float_positional(
                row["dust"],
                fractional=True,
                trim="k",
                precision=2,
                min_digits=2,
            ),
            "---"
            if row["background"].mask
            else np.format_float_positional(
                row["background"],
                fractional=True,
                trim="k",
                precision=2,
                min_digits=2,
            ),
            "---"
            if row["detection_prob"].mask
            else np.format_float_positional(
                row["detection_prob"],
                fractional=True,
                trim="k",
                precision=2,
                min_digits=2,
            ),
            sep=" & ",
            end=" \\\\\n" if i < len(plan) - 1 else "\n",
            file=f,
        )
