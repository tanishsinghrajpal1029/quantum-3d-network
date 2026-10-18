#!/bin/bash
# Pilot 1 on a Mac (exploratory): all 3 lattices at once, 5 workers each (15 processes; leave a few cores free).
# Run from sim/:  caffeinate -i bash tools/run_pilot1_mac.sh      Resume-safe: re-running skips finished runs.
cd "$(dirname "$0")/.." || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p out/pilot1
NW=5
for L in d2g11 d3g5 d2g13; do
  D=${L:1:1}; G=${L#*g}
  for ((w=0; w<NW; w++)); do
    P3D_D=$D P3D_GRID=$G python3 tools/pilot1.py $w $NW out/pilot1/mac_${L}_w$w.csv > out/pilot1/mac_${L}_w$w.log 2>&1 &
  done
done
echo "started 15 workers at $(date); waiting..."
wait
n=$(cat out/pilot1/mac_*_w*.csv 2>/dev/null | grep -vc '^run,')
echo "PILOT1 DONE: $n of 72 runs at $(date)" | tee out/pilot1/MAC_DONE
