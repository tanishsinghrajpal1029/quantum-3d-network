#!/bin/bash
#SBATCH --job-name=p3d-check2
#SBATCH --partition=RM-shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=00:50:00
#SBATCH --output=check_v2_%j.log
# Study 3D-2 gate (docs/PREREG_3D2.md), on PSC with the frozen fork v2: (a) the default path reproduces 4 Study 34 runs and
# (b) lazy users (P3D_LAZY=1) reproduce 2 of them, all 83 columns. Run from sim/psc3d2:
#   sbatch --account=<charge-id> --export=ALL,PY=<python3> check_v2.sbatch          (about 5 SU)
set -euo pipefail
: "${PY:?}"
cd "$SLURM_SUBMIT_DIR/.."
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p out/check_v2
for L in 1 161 673 1000; do
  "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl --lines $L \
    --ref reference/s34_g5_runs.csv --out out/check_v2/e$L.csv > out/check_v2/e$L.log 2>&1 &
done
for L in 1 673; do
  P3D_LAZY=1 "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl --lines $L \
    --ref reference/s34_g5_runs.csv --out out/check_v2/z$L.csv > out/check_v2/z$L.log 2>&1 &
done
wait
cat out/check_v2/e*.log out/check_v2/z*.log
n=$(grep -c "MATCH (all 83 columns)" out/check_v2/e*.log out/check_v2/z*.log | awk -F: '{s+=$2} END {print s}')
echo "GATE: $n of 6 runs match Study 34 exactly (4 default + 2 lazy users)"
[ "$n" = 6 ] && echo "GATE PASS: go ahead with the confirmatory jobs" || echo "GATE FAIL: STOP, do not run the confirmatory jobs"
