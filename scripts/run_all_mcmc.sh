#!/bin/bash

cd "$(dirname "$0")/.."

echo "Starting the MCMC Job Quene ..."
echo "Running up to 3 jobs simultaneously (12 cores total) ..."
echo "Check the logs/ folder for progress."

# Find all YAML files and queue them
find inputs/ -type f -name "*.yaml" | xargs -I {} -P 3 bash -c '
    filename=$(basename "{}")
    logfile="logs/${filename}.log"
    lockfile="logs/${filename}.lock"

    if grep -q "\[STATUS: COMPLETED\]" "$logfile" 2>/dev/null; then
        echo "Skipping ${filename} (already completed)"
        exit 0
    fi

    flock -n "$lockfile" bash -c "mpirun -n 4 cobaya-run -r \"{}\" >> \"$logfile\" 2>&1 && echo \"[STATUS: COMPLETED]\" >> \"$logfile\""
'

echo "All jobs have been queued. Check the logs/ folder for progress."
