#!/bin/bash
#SBATCH --job-name=p3d-check3
#SBATCH --partition=RM-shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:50:00
#SBATCH --output=check_v3_%j.log
# Study 3D-3 gate (docs/PREREG_3D3.md), on PSC with the frozen fork v3: 2 Study 34 runs on the default path, 1 with lazy users,
# and 1 Study 3D-2 confirmatory run (2D 32x32, fut97, kg, network 0) must match their recorded rows in every column.
# Run from sim/psc3d3:  sbatch --account=<charge-id> --export=ALL,PY=<python3> check_v3.sbatch       (about 4 SU)
set -euo pipefail
: "${PY:?}"
cd "$SLURM_SUBMIT_DIR/.."
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p out/check_v3
for L in 1 161; do
  "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl --lines $L \
    --ref reference/s34_g5_runs.csv --out out/check_v3/e$L.csv > out/check_v3/e$L.log 2>&1 &
done
P3D_LAZY=1 "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks upstream/tasks_s34_g5.jsonl --lines 1 \
  --ref reference/s34_g5_runs.csv --out out/check_v3/z1.csv > out/check_v3/z1.log 2>&1 &
P3D_REACH=1 "$PY" tools/repro_check.py --module study3d --lib fork:upstream --tasks psc3d2/tasks_3d2_d2g32.jsonl --lines 1 \
  --ref reference/s3d2_d2g32_runs.csv --out out/check_v3/r1.csv > out/check_v3/r1.log 2>&1 &
wait
cat out/check_v3/*.log
n=$(grep -c "ALL MATCH" out/check_v3/*.log | awk -F: '{s+=$2} END {print s}')
echo "GATE: $n of 4 runs reproduced exactly (2 default + 1 lazy users + 1 Study 3D-2 reach run)"
[ "$n" = 4 ] && echo "GATE PASS: go ahead with the confirmatory jobs" || echo "GATE FAIL: STOP, do not run the confirmatory jobs"
