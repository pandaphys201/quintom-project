import glob
import os
import yaml
from getdist import loadMCSamples
from cobaya.run import run
from pathlib import Path

# ========================================================================================
# Define a function to run the minimizer for each chain
# ========================================================================================

def run_minimizer(old_chain_root, yaml_config_path):
    print("Extracting best MCMC sample...")
    samples = loadMCSamples(old_chain_root)
    best_mcmc_sample = samples.getParamBestFitDict(best_sample=True, max_posterior=True)

    # 3. Load your original Cobaya configuration
    with open(yaml_config_path, 'r') as file:
        info = yaml.safe_load(file)

    # 4. Inject the best sample as the starting point ('ref')
    print("Updating starting points...")
    for param_name, param_value in best_mcmc_sample.items():
        # We only update sampled parameters (they have a 'prior' block)
        # GetDist also returns derived parameters, which we must skip
        if param_name in info.get('params', {}):
            param_block = info['params'][param_name]
            if isinstance(param_block, dict) and 'prior' in param_block:
                # Set the starting point to the exact float from GetDist
                info['params'][param_name]['ref'] = float(param_value)
                print(f"  -> Set {param_name} starting point to {float(param_value)}")

    # 5. Replace the 'mcmc' sampler with 'minimize'
    info['sampler'] = {
        'minimize': {
            'ignore_prior': False,      # False = Maximum Posterior, True = Maximum Likelihood
            'max_evals': 10000,         # Safety limit to prevent infinite loops
            "confidence_for_unbounded": 0.9999999
        }
    }

    info['debug'] = True  # Optional: Enable debug mode for more verbose output

    chain_name = os.path.dirname(old_chain_root)
    info['output'] = f"{chain_name}/temp_minimizer"

    # 7. Run the minimizer
    print("Starting Cobaya minimizer...")
    
    try: 
        updated_info, sampler = run(info)
    except Exception as e:
        print(f"Error during minimization: {e}")

    # 8. Safely rename the .minimum file to match your MCMC chains
    temp_min_file = f"{info['output']}.minimum"
    final_min_file = f"{old_chain_root}.minimum"

    if os.path.exists(temp_min_file):
        # This moves and renames the file
        os.rename(temp_min_file, final_min_file)
        print(f"\nSuccess! Saved best-fit to: {final_min_file}")

        # Optional: Clean up the temporary yaml files the minimizer generated
        files_to_delete = glob.glob(f"{info['output']}*")
        for file in files_to_delete:
            os.remove(file)
    else:
        print("Error: Minimizer did not produce a .minimum file.")

if __name__ == "__main__":
    chains = {}
    root = Path(r'/home/theppawan/cosmo-research/quintom-project')
    chain_dir = root/'chains'
    chain_prefixes = [p.with_suffix('') for p in chain_dir.rglob('*.checkpoint')]

    for prefix_path in chain_prefixes:
        chain_name = prefix_path.name
        model, dataset = chain_name.split("_", 1)
        chains[chain_name] = [str(prefix_path), str(root/'inputs'/f'{chain_name}.yaml')]

    run_minimizer(old_chain_root=chains['quintom_DESI+CMB+SNIa+SH0ES'][0],
                  yaml_config_path=chains['quintom_DESI+CMB+SNIa+SH0ES'][1])

    ## quintom_DESI+CMB+SNIa+SH0ES --> Segmentation fault (core dumped) 