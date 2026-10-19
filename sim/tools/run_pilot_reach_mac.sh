#!/bin/bash
# Reach pilot on a Mac (exploratory): 3 lattices x 24 tasks. Each process needs about 2.3 GB, so the number of workers per
# lattice is chosen from the Mac's memory (about 3 GB per worker, at most 5 per lattice). Run from sim/:
#   caffeinate -i bash tools/run_pilot_reach_mac.sh        Resume-safe: re-running skips finished runs.
cd "$(dirname "$0")/.." || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 P3D_REACH=1
mkdir -p out/pilot_reach
MEM_GB=$(( $(sysctl -n hw.memsize) / 1073741824 )); NW=$(( MEM_GB / 3 / 3 )); [ $NW -gt 5 ] && NW=5; [ $NW -lt 1 ] && NW=1
echo "memory ${MEM_GB} GB -> ${NW} workers per lattice ($((3 * NW)) in total); started $(date)"
for L in d2g32 d3g10 d2g37; do
  D=${L:1:1}; G=${L#*g}
  for ((w=0; w<NW; w++)); do
    P3D_D=$D P3D_GRID=$G python3 tools/pilot_reach.py $w $NW out/pilot_reach/mac_${L}_w$w.csv > out/pilot_reach/mac_${L}_w$w.log 2>&1 &
  done
done
wait
n=$(cat out/pilot_reach/mac_*_w*.csv 2>/dev/null | grep -vc '^run,')
echo "REACH PILOT DONE: $n of 72 runs at $(date)" | tee out/pilot_reach/MAC_DONE
grep -il "error\|traceback" out/pilot_reach/*.log && echo "SOME WORKERS FAILED: see the logs above"
