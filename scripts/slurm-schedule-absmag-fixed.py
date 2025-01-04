#!/usr/bin/env python
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH -N1 -n1
#SBATCH -t 2-00:00
"""Run the M4OPT scheduler on a batch of sky maps on the SDSC Expanse cluster
(https://www.sdsc.edu/services/hpc/expanse/)."""

job_cpu = 8
event_id = 800


def task(exptime_s):
    from unittest.mock import patch
    from m4opt._cli import app
    import shlex
    args = shlex.split(f"schedule --mission=uvex --bandpass=NUV --deadline=6hour --timelimit=2hour --exptime-min={exptime_s}s --nside=128 --jobs={job_cpu} {event_id}.fits {event_id}-exptime-{exptime_s}s.ecsv")
    try:
        with (
            open(f"{event_id}-exptime-{exptime_s}s.out", mode="w") as outerr,
            patch("sys.stdout", outerr),
            patch("sys.stderr", outerr),
        ):
            app(args)
    except SystemExit as e:
        if e.code != 0:
            raise RuntimeError(f"Process exited with code {e.code}")


if __name__ == '__main__':
    from pathlib import Path
    from dask_jobqueue import SLURMCluster
    from distributed import as_completed
    from tqdm.auto import tqdm

    walltime = 48 * 60
    max_workers = 32
    exptime_s = list(range(300, 3700, 100))

    with SLURMCluster(
        account="umn131",
        cores=1,
        job_cpu=job_cpu,
        job_extra_directives=["--nodes=1"],
        job_script_prologue=[f"export OMP_NUM_THREADS={job_cpu}"],
        memory="16GiB",
        processes=1,
        queue="shared",
        walltime=str(walltime),
        worker_extra_args=["--lifetime", f"{walltime - 5}m", "--lifetime-stagger", "4m"],
    ) as cluster, cluster.get_client() as client:
        print(cluster.job_script())
        cluster.adapt(maximum=max_workers)
        for future in tqdm(as_completed(client.map(task, exptime_s)), total=len(exptime_s)):
            future.result()
