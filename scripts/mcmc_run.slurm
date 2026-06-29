#!/bin/bash
#SBATCH --job-name=cobaya_mcmc
#SBATCH --output=logs/job_%A_task_%a.out
#SBATCH --error=logs/job_%A_task_%a.err
#SBATCH --nodes=1
#SBATCH --qos=cu_hpc                      # Specifies your exact QoS tier
#SBATCH --ntasks=4                        # 4 MPI processes per YAML file (ideal for 4 MCMC chains)
#SBATCH --cpus-per-task=1                 # 1 CPU core per MPI task
#SBATCH --mem=16G                         # Safe memory allocation per job
#SBATCH --time=14-00:00:00                # Maximized to the 14-day limit for deep convergence
#SBATCH --array=1-50%20                   # Array size (e.g., 50 files) running exactly 20 at a time!

# ==========================================
# 1. Load Environment & Modules
# ==========================================
module purge
module load OpenMPI 
module load Python    
# source path/to/your/venv/bin/activate

# ==========================================
# 2. Map Array ID to Input File
# ==========================================
FILES=(inputs/*.yaml)
INDEX=$((SLURM_ARRAY_TASK_ID - 1))

if [ $INDEX -ge ${#FILES[@]} ]; then
    echo "No input file for index $INDEX. Exiting."
    exit 0
fi

INPUT_YAML=${FILES[$INDEX]}
FILENAME=$(basename "$INPUT_YAML")
LOGFILE="logs/${FILENAME}.log"

# ==========================================
# 3. Resume / Run Logic
# ==========================================
echo "========================================"
echo " Starting Task: $FILENAME"
echo " SLURM Job Array ID: $SLURM_ARRAY_JOB_ID, Task ID: $SLURM_ARRAY_TASK_ID"
echo "========================================"

if grep -q "\[STATUS: COMPLETED\]" "$LOGFILE" 2>/dev/null; then
    echo "[DONE]: ${FILENAME} (Skipping)"
    exit 0
fi

echo "[STARTING | RESUMING]: ${FILENAME}"

# srun is generally preferred over mpirun on SLURM for better resource tracking
srun -n 4 cobaya-run -r "$INPUT_YAML" >> "$LOGFILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[STATUS: COMPLETED]" >> "$LOGFILE"
    echo "[FINISHED]: ${FILENAME}"
else
    echo "[STOPPED | CRASHED]: ${FILENAME} (Check its log file)"
fi