from cobaya.likelihood import Likelihood
import numpy as np
import scipy.linalg as cho
import os

class CMB_Distance_Prior_wcdm(Likelihood):

    def initialize(self):
        """
            Importing Data Observations
        """
        self.mean_data = np.array([1.7493, 301.462, 0.02239])
        self.std_data = np.array([0.00465, 0.0895, 0.00015])
        self.norm_cov = np.array([
            [1, 0.47, -0.66],
            [0.47, 1, -0.34],
            [-0.66, -0.34, 1]
        ])
        self.cov = np.diag(self.std_data) @ self.norm_cov @ np.diag(self.std_data)
        self.L = cho.cholesky(self.cov, lower=True)

    def get_requirements(self):
        """
            Asking for specific quantities from a theory code
        """
        return {
            "omega_b": None,
            "omega_cdm": None,
            "z_rec": None,
            "rs_rec": None,
            "da_rec": None
        }

    def logp(self, **params_values):
        """
            Calculating the Log-Likelihood
        """
        omega_b = self.provider.get_param('omega_b')
        omega_cdm = self.provider.get_param('omega_cdm')
        rs_rec = self.provider.get_param('rs_rec')
        da_rec = self.provider.get_param('da_rec')
        z_rec = self.provider.get_param('z_rec')

        c = 299792.458 # Speed of light in km/s
        # Comoving distance to recombination
        r_rec = (1.0 + z_rec) * da_rec
        # Calculate the Shift paramter (R) and acoustic scale (l_a)
        R_th = r_rec * 100 * np.sqrt(omega_b + omega_cdm) / c
        l_a_th = np.pi * r_rec / rs_rec

        diff = np.array([R_th, l_a_th, omega_b]) - self.mean_data
        mahalanobis_dist = cho.cho_solve((self.L, True), diff)
        chi2 = np.dot(diff, mahalanobis_dist)

        return -0.5 * chi2

class CMB_Distance_Prior_lcdm(Likelihood):

    def initialize(self):
        """
            Importing Data Observations
        """
        self.mean_data = np.array([1.7502, 301.471, 0.02236])
        self.std_data = np.array([0.0046, 0.0895, 0.00015])
        self.norm_cov = np.array([
            [1, 0.46, -0.66],
            [0.46, 1, -0.33],
            [-0.66, -0.33, 1]
        ])
        self.cov = np.diag(self.std_data) @ self.norm_cov @ np.diag(self.std_data)
        self.L = cho.cholesky(self.cov, lower=True)

    def get_requirements(self):
        """
            Asking for specific quantities from a theory code
        """
        return {
            "omega_b": None,
            "omega_cdm": None,
            "z_rec": None,
            "rs_rec": None,
            "da_rec": None
        }

    def logp(self, **params_values):
        """
            Calculating the Log-Likelihood
        """
        omega_b = self.provider.get_param('omega_b')
        omega_cdm = self.provider.get_param('omega_cdm')
        rs_rec = self.provider.get_param('rs_rec')
        da_rec = self.provider.get_param('da_rec')
        z_rec = self.provider.get_param('z_rec')

        c = 299792.458 # Speed of light in km/s
        # Comoving distance to recombination
        r_rec = (1.0 + z_rec) * da_rec
        # Calculate the Shift paramter (R) and acoustic scale (l_a)
        R_th = r_rec * 100 * np.sqrt(omega_b + omega_cdm) / c
        l_a_th = np.pi * r_rec / rs_rec

        diff = np.array([R_th, l_a_th, omega_b]) - self.mean_data
        mahalanobis_dist = cho.cho_solve((self.L, True), diff)
        chi2 = np.dot(diff, mahalanobis_dist)

        return -0.5 * chi2  