#!/bin/bash

cd "$(dirname "$0")/.."

echo "========================================"
echo "   Starting the Smart MCMC Job Queue"
echo "========================================"
echo "Queue capacity: 3 jobs simultaneously (12 cores total)."
echo "Status updates will appear below..."
echo "----------------------------------------"

find inputs/ -type f -name "*.yaml" | xargs -I {} -P 3 bash -c '
    filename=$(basename "{}")
    logfile="logs/${filename}.log"
    lockfile="logs/${filename}.lock"
   
    if grep -q "\[STATUS: COMPLETED\]" "$logfile" 2>/dev/null; then
        echo "DONE: ${filename}"
        exit 0
    fi
    (
        if flock -n 9; then
            echo "STARTING / RESUMING: ${filename}"
            mpirun -n 4 cobaya-run -r "{}" >> "$logfile" 2>&1
           
            if [ $? -eq 0 ]; then
                echo "[STATUS: COMPLETED]" >> "$logfile"
                echo "JUST FINISHED: ${filename}"
            else
                echo "STOPPED / CRASHED: ${filename} (Check its log file)"
            fi
        else
            echo "CURRENTLY RUNNING: ${filename}"
        fi
    ) 9>> "$lockfile"
'

echo "----------------------------------------"
echo "Queue check complete! All discovered jobs processed."