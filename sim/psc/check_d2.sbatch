#!/bin/bash
#SBATCH --job-name=p3d-check
#SBATCH --partition=RM-shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:45:00
#SBATCH --output=check_d2_%j.log
# Study 3D-1 gate (docs/PREREG_3D1.md): on PSC, the fork at d = 2 must reproduce 4 Study 34 runs in all 83 columns.
# Run from sim/psc:  sbatch --account=<charge-id> --export=ALL,PY=<python3> check_d2.sbatch      (about 4 SU)
set -euo pipefail
: "${PY:?}"
cd "$SLURM_SUBMIT_DIR/.."
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p out/check_d2
for L in 1 161 673 1000; do
  "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl --lines $L \
    --ref reference/s34_g5_runs.csv --out out/check_d2/l$L.csv > out/check_d2/l$L.log 2>&1 &
done
wait
cat out/check_d2/l*.log
n=$(grep -c "MATCH (all 83 columns)" out/check_d2/l*.log | awk -F: '{s+=$2} END {print s}')
echo "GATE: $n of 4 runs match Study 34 exactly"; [ "$n" = 4 ] && echo "GATE PASS: go ahead with the confirmatory jobs" || echo "GATE FAIL: STOP, do not run the confirmatory jobs"
