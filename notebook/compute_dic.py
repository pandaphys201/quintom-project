import numpy as np
from getdist import loadMCSamples
from cobaya.model import get_model
from cobaya.yaml import yaml_load
from pathlib import Path

def compute_dic(chain_prefix, burnin_fraction=0.3):
    """
    Computes the Deviance Information Criterion (DIC) for a Cobaya MCMC run.
    """
    print(f"Loading chains for prefix: {chain_prefix}")
    
    samples = loadMCSamples(chain_prefix, settings={'ignore_rows': burnin_fraction})
    param_names = samples.getParamNames().list()

    yaml_file = f"{chain_prefix}.updated.yaml"
    print(f"Loading Cobaya model from: {yaml_file}")
    
    with open(yaml_file, 'r') as f:
        info = yaml_load(f)

    likelihood_dict = info.get('likelihood', {})
    expected_chi2_cols = [f"chi2__{name}" for name in likelihood_dict.keys()]

    chi2_cols = [col for col in expected_chi2_cols if col in param_names]

    print(f"Dynamically summing the following chi2 columns: {chi2_cols}")
    if chi2_cols:
        deviance_chain = np.zeros(samples.samples.shape[0])
        for col in chi2_cols:
            idx = param_names.index(col)
            deviance_chain += samples.samples[:, idx]
    else:
        idx_post = param_names.index('minuslogpost')
        minuslogpost = samples.samples[:, idx_post]
        
        if 'minuslogprior' in param_names:
            idx_prior = param_names.index('minuslogprior')
            minuslogprior = samples.samples[:, idx_prior]
            deviance_chain = 2.0 * (minuslogpost - minuslogprior)
        else:
            deviance_chain = 2.0 * minuslogpost
            
    mean_deviance = np.average(deviance_chain, weights=samples.weights)
    
    sampled_params = [p for p, p_info in info.get('params', {}).items() 
                      if isinstance(p_info, dict) and 'prior' in p_info]
                      
    mean_params = {}
    for p in sampled_params:
        if p in param_names:
            idx = param_names.index(p)
            p_array = samples.samples[:, idx]
            mean_params[p] = float(np.average(p_array, weights=samples.weights))
        else:
            print(f"Warning: Sampled parameter '{p}' not found in chain columns.")
        
    print(f"Evaluated Mean Parameters: {mean_params}")
    
    model = get_model(info)
    print("\nRunning CLASS and likelihoods at mean parameters... (this may take a moment)")
    
    logpost_obj = model.logposterior(mean_params)
    
    if hasattr(logpost_obj, 'loglike'):
        loglike_at_mean = logpost_obj.loglike
    elif hasattr(logpost_obj, 'loglkl'):
        loglike_at_mean = logpost_obj.loglkl
    else:
        loglike_at_mean = logpost_obj[1] 
        
    if not np.isfinite(loglike_at_mean):
        print("Warning: Model evaluation at the mean parameters failed (returned -inf).")
        return None
        
    deviance_at_mean = -2.0 * loglike_at_mean
    
    p_D = mean_deviance - deviance_at_mean
    dic = deviance_at_mean + 2.0 * p_D
    
    print("\n" + "="*40)
    print(f"Mean Deviance ( D-bar )         : {mean_deviance:.2f}")
    print(f"Deviance at mean ( D(theta_bar) ): {deviance_at_mean:.2f}")
    print(f"Effective parameters ( p_D )    : {p_D:.2f}")
    print(f"DIC                             : {dic:.2f}")
    print("="*40 + "\n")
    
    return dic, p_D

if __name__ == "__main__":
    # Replace with the path/prefix to your MCMC chains
    chain_dir = Path(r'/home/theppawan/cosmo-research/quintom-project/chains')
    compute_dic(str(chain_dir / 'quintom/DESI+CMB+SNIa/quintom_DESI+CMB+SNIa'), burnin_fraction=0.3)