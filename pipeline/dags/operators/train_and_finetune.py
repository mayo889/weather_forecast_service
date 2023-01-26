import numpy as np
import pandas as pd
from os import path 
from prophet import Prophet
from prophet.serialize import model_from_json, model_to_json

from .db_tools import read_data_from_col 
from .paths import MODEL_FILENAME, MODEL_PATH


MODEL_PARAMS = {              
    'changepoint_prior_scale': 0.15,
    'seasonality_prior_scale': 5,
    'holidays_prior_scale': 0,
    'seasonality_mode': 'additive',
    'changepoint_range': 0.8,
    'yearly_seasonality': True,
    'weekly_seasonality': False,
    'daily_seasonality': False
}


def get_stan_init(m):
    res = {}
    for pname in ['k', 'm', 'sigma_obs']:
        if m.mcmc_samples == 0:
            res[pname] = m.params[pname][0][0]
        else:
            res[pname] = np.mean(m.params[pname])
    for pname in ['delta', 'beta']:
        if m.mcmc_samples == 0:
            res[pname] = list(m.params[pname][0]) 
        else:
            res[pname] = list(np.mean(m.params[pname], axis=0)) 
    return res


def train_and_save(finetune=False): 
    df = pd.DataFrame(read_data_from_col('history'))
    if finetune: 
        with open(path.join(MODEL_PATH, MODEL_FILENAME), 'r') as fin:
            saved_model = model_from_json(fin.read())  # Load model

        m_fine_tuned = Prophet(**MODEL_PARAMS).fit(df, inits=get_stan_init(saved_model))  

        finetuned_model = model_to_json(m_fine_tuned)

        with open(path.join(MODEL_PATH, MODEL_FILENAME), 'w') as fout:
            fout.write(finetuned_model)  # Save model
    else: 
        m = Prophet(**MODEL_PARAMS).fit(df) 
        with open(path.join(MODEL_PATH, MODEL_FILENAME), 'w') as fout:
            fout.write(model_to_json(m))
