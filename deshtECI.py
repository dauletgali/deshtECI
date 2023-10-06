# importing the sys module
#import sys        
 
# appending the directory of mod.py
# in the sys.path list
#sys.path.append(r"ecoci_b")       

import econci
import pandas as pd

class deshtEci(econci.Complexity):

    def __init__(self, df: pd.DataFrame, c: str, p: str, values: str, m_cp_thresh: float = 1, manual:bool=False):
        super().__init__(df, c, p, values, m_cp_thresh)
        self.manual = manual
        if manual == True:
            #check for 0 , 1 if manual 
            if not (df[values].min() == 0) & (df[values].max() == 1):
                print('It is not 0 and 1')
            m_cp = df.pivot(index=c , columns=p , values=values).fillna(0)
            if m_cp.sum(axis=1).min() == 0:
                print('There is 0 diversity will be dropped '  , m_cp.sum(axis=1).loc[lambda x: x==0])
            if m_cp.sum(axis=0).min() == 0 :
                print('There is 0 ubiquity it will be dropped for calculations' , m_cp.sum(axis=0).loc[lambda x: x==0])
#             m_cp = m_cp[(m_cp != 0).all(axis=0).index]
#             m_cp = m_cp.loc[(m_cp != 0).all(axis=1).index]
            m_cp = m_cp.loc[(m_cp.sum(axis=1)!= 0), (m_cp.sum(axis=0) != 0)]

            self._m_cp = m_cp
            self._m = m_cp
    
    def calculate_indexes(self):
        if self.manual == True:
            self._get_diversity()
            self._get_ubiquity()
            self._calc_eci()
            self._calc_pci()
            self._calc_proximity()
            self._calc_density()
            self._calc_distance()
        else:
            super().calculate_indexes()




#data = pd.read_csv('res.csv')
#index = deshtEci(data, c='Country', p='com_class', values='rca_1_net_exp', manual=True )
#index.calculate_indexes()
#index._generate_graphs()
#mx_tr = index._maxst
#econci.edges_nodes_to_csv(mx_tr, 'mx_tree', '.')