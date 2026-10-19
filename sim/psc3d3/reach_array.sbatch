#!/bin/bash
#SBATCH --job-name=p3d-reach
#SBATCH --partition=RM-shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=s18c-logs/reach_%A_%a.out
#SBATCH --error=s18c-logs/reach_%A_%a.err
# Study 3D-2 (reach) array job (docs/PREREG_3D2.md). One array element = one shard of one lattice's task list.
# Memory: a 3D 10^3 or 2D 37x37 run peaks at about 3 GB and RM-shared gives about 2 GB per core, so WORKERS can be fewer
# than the cores requested. Required: --export=ALL,P3D_REACH=1,P3D_D=..,P3D_GRID=..,PY=..,TASKS=..,OUT=..,NSHARDS=..,WORKERS=..
set -euo pipefail
: "${P3D_REACH:?}"; : "${P3D_D:?}"; : "${P3D_GRID:?}"; : "${PY:?}"; : "${TASKS:?}"; : "${OUT:?}"; : "${NSHARDS:?}"; : "${WORKERS:?}"
cd "$SLURM_SUBMIT_DIR"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH="$SLURM_SUBMIT_DIR/../fork"
"$PY" psc_array_runner.py --module study3d --tasks "$TASKS" --outdir "$OUT" --shard "$SLURM_ARRAY_TASK_ID" --nshards "$NSHARDS" --workers "$WORKERS"
