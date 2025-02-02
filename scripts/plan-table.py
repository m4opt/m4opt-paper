from astropy.table import QTable
import numpy as np
from astropy import units as u

table = QTable.read("data/O5/3628.ecsv")
table["start_time"].precision = 0
with open("tables/3628.tex", "w") as f:
    for i, row in enumerate(table):
        print(
            row["start_time"],
            int(np.rint(row["duration"].to_value(u.s))),
            row["action"],
            "---"
            if row["observer_location"].mask
            else int(np.rint(
                row["observer_location"].geocentric[0].to_value(u.km))),
            "---"
            if row["observer_location"].mask
            else int(np.rint(
                row["observer_location"].geocentric[1].to_value(u.km))),
            "---"
            if row["observer_location"].mask
            else int(np.rint(
                row["observer_location"].geocentric[2].to_value(u.km))),
            "---"
            if row["target_coord"].mask
            else np.format_float_positional(
                row["target_coord"].ra.deg, fractional=True, trim="k", precision=4, min_digits=4,
            ),
            "---"
            if row["target_coord"].mask
            else np.format_float_positional(
                row["target_coord"].dec.deg, fractional=True, trim='k', precision=4, min_digits=4, sign=True
            ),
            "---"
            if row["roll"].mask
            else int(np.rint(
                row["roll"].to_value(u.deg))),
            sep=" & ",
            end=' \\\\\n' if i < len(table) - 1 else '\n',
            file=f,
        )
