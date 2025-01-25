from pathlib import Path
from detection_probability import get_detection_probability_known_position
from astropy.cosmology import Planck15 as cosmo, z_at_value
from astropy import units as u

base_path = Path("runs_SNR-10")


def process(row):
    run = row["run"]
    event_id = row["coinc_event_id"]
    plan = QTable.read(
        base_path / f"{run}HLVK" / "farah" / "allsky" / f"{event_id}.ecsv"
    )
    plan_args = {**plan.meta["args"]}
    plan_args.pop("skymap")
    return get_detection_probability_known_position(plan, row, plan_args), plan.meta[
        "objective_value"
    ]


if __name__ == "__main__":
    from astropy.table import QTable, join, vstack
    import numpy as np
    from ligo.skymap.util.progress import progress_map

    runs = ["O5", "O6"]

    # Read summary data for all events
    tables = []
    for run in runs:
        run_dir = base_path / f"{run}HLVK" / "farah"
        table = join(
            QTable.read(run_dir / "allsky.dat", format="ascii"),
            QTable.read(run_dir / "injections.dat", format="ascii"),
        )
        assert (table["coinc_event_id"] == np.arange(len(table))).all()
        table["run"] = run
        table.meta.clear()
        tables.append(table)
    table = vstack(tables)
    del tables

    # Throw away BBHs
    z = z_at_value(cosmo.luminosity_distance, table["distance"] * u.Mpc).to_value(
        u.dimensionless_unscaled
    )
    max_mass2 = 3
    table = table[table["mass2"] <= max_mass2 * (1 + z)]

    table["detection_probability_known_position"], table["objective_value"] = zip(
        *progress_map(process, table)
    )

    table.write("tables/events.ecsv", overwrite=True)
