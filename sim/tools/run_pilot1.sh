#!/bin/bash
# Runs Pilot 1 on two cores, one lattice at a time (each process builds one lattice at import).
cd "$(dirname "$0")/.."; mkdir -p out/pilot1
for L in "2 11" "3 5" "2 13"; do
  set -- $L
  for w in 0 1; do P3D_D=$1 P3D_GRID=$2 python3 tools/pilot1.py $w 2 out/pilot1/d$1g$2_w$w.csv >> out/pilot1/d$1g$2_w$w.log 2>&1 & done
  wait
done
echo PILOT1 DONE > out/pilot1/DONE
