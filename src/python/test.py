import numpy as np
import pandas as pd
from itertools import chain, combinations
from src.python.models import OLSRobust
import warnings
warnings.filterwarnings("ignore")

union_df = pd.read_stata('./data/input/nlsw88.dta')

union_df.loc[:, 'log_wage'] = np.log(union_df['wage'].copy())*100
union_df = union_df[union_df['union'].notnull()].copy()
union_df.loc[:, 'union'] = np.where(union_df['union'] == 'union', 1, 0)
union_df.loc[:, 'married'] = np.where(union_df['married'] == 'married', 1, 0)
union_df.loc[:, 'collgrad'] = np.where(union_df['collgrad'] == 'college grad', 1, 0)
union_df.loc[:, 'smsa'] = np.where(union_df['smsa'] == 'SMSA', 1, 0)
indep_list = ['hours', 'age',
              'grade', 'collgrad', 'married',
              'south', 'smsa', 'c_city', 'ttl_exp',
              'tenure']
for var in indep_list:
    union_df = union_df[union_df[var].notnull()]
y = pd.DataFrame(union_df['log_wage'])
c = union_df[indep_list]
x = pd.DataFrame(union_df['union'])

def get_mspace(varnames) -> list:
    model_space = []

    def all_subsets(ss):
        return chain(*map(lambda x: combinations(ss, x),
                          range(0, len(ss) + 1)))

    for subset in all_subsets(varnames):
        model_space.append(subset)
    return model_space

control_list = c.columns.to_list()
model_space = get_mspace(control_list)

myrobust = OLSRobust(x, y)   

beta, p, aic, bic = myrobust.fit(c=c, space=model_space, s=100, mode='simple')


########


ASC_df = pd.read_stata('CleanData_LASpending.dta', convert_categoricals=False)

one_hot = pd.get_dummies(ASC_df['year'])
ASC_df = ASC_df.join(one_hot)
ASC_df = ASC_df.set_index(['pidp','year'])
ASC_df['dcareNew*c.lrealgs'] = ASC_df['dcareNew']*ASC_df['lrealgs']
ASC_df['constant'] = 1
y = ASC_df['wellbeing_kikert']
x = ASC_df['lrealgs']
c = ASC_df[['dcareNew*c.lrealgs',
            'dcareNew',
            'DR',
            'lgva',
            'hhsize',
            'work',
            'retired',
            2005.0,
            ]]

control_list = c.columns.to_list()
model_space = get_mspace(control_list)

myrobust_panel = OLSRobust(x, y)
beta, p, aic, bic = myrobust_panel.fit(c=c, space=model_space, s=10, mode='panel')

pd.DataFrame(beta)