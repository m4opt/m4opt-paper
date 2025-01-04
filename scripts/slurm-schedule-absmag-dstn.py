#!/usr/bin/env python
#SBATCH --partition=shared
#SBATCH --account=umn131
#SBATCH -N1 -n1
#SBATCH -t 2-00:00
"""Run the M4OPT scheduler on a batch of sky maps on the SDSC Expanse cluster
(https://www.sdsc.edu/services/hpc/expanse/)."""

job_cpu = 8


def task(task_id):
    from unittest.mock import patch
    from m4opt._cli import app
    import shlex
    args = shlex.split(f"schedule --mission=uvex --bandpass=NUV --deadline=6hour --timelimit=2hour --absmag-mean=-14 --absmag-stdev=1 --exptime-min=300s --nside=128 --cutoff=0.1 --jobs={job_cpu} {task_id}.fits {task_id}.ecsv")
    try:
        with (
            open(f"{task_id}.out", mode="w") as outerr,
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
    max_workers = 256
    num_tasks = max(int(path.stem) for path in Path('.').glob('*.fits')) + 1

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
        for future in tqdm(as_completed(client.map(task, range(num_tasks))), total=num_tasks):
            future.result()
