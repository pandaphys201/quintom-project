import numpy as np
from getdist import loadMCSamples
from cobaya.model import get_model
from cobaya.yaml import yaml_load
from pathlib import Path

def compute_dic(chain_prefix, burnin_fraction=0.3): 
    samples = loadMCSamples(chain_prefix, settings={'ignore_rows': burnin_fraction})
    # compute Mean D(theta)
    param_names = samples.getParamNames().list()
    idx_chi2 = param_names.index('chi2')
    deviance_chain = samples.samples[:, idx_chi2]
    mean_deviance = np.average(deviance_chain, weights=samples.weights)

    # compute chi_sq_MAP for D(mean theta)
    yaml_file = f"{chain_prefix}.updated.yaml"   
    with open(yaml_file, 'r') as f:
        info = yaml_load(f)
    likelihood_dict = info.get('likelihood', {})
    expected_chi2_cols = [f"chi2__{name}" for name in likelihood_dict.keys()]
    best_fit_params = samples.getParamBestFitDict(best_sample=False)
    chi2_cols = [col for col in expected_chi2_cols if col in best_fit_params.keys()]
    deviance_at_map = 0
    for chi2_i in chi2_cols:
        deviance_at_map += best_fit_params[chi2_i]

    p_D = mean_deviance - deviance_at_map
    dic = deviance_at_map + 2.0 * p_D
    
    # print("\n" + "="*40)
    # print(f"Mean Deviance ( D-bar )         : {mean_deviance:.2f}")
    # print(f"Deviance at mean ( D(theta_bar) ): {deviance_at_mean:.2f}")
    # print(f"Effective parameters ( p_D )    : {p_D:.2f}")
    # print(f"DIC                             : {dic:.2f}")
    # print("="*40 + "\n")
    
    return dic, p_D

if __name__ == "__main__":
    # Replace with the path/prefix to your MCMC chains
    chain_dir = Path(r'/home/theppawan/cosmo-research/quintom-project/chains')
    compute_dic(str(chain_dir / 'lcdm/DESI+CMB+SNIa/lcdm_DESI+CMB+SNIa'), burnin_fraction=0.3)