# importing the sys module
#import sys        
 
# appending the directory of mod.py
# in the sys.path list
#sys.path.append(r"ecoci_b")       

import econci
import pandas as pd
import numpy as np
import networkx as nx
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
    
    def _calc_average_proximity(self):
        """
        Calculate proxoimity based on average of two baskets
        """
        kp0 = self._ubiquity
        phi = self._m_cp.T.dot(self._m_cp)
        #phi_pp = phi.apply(lambda x : x / np.mean(kp0.loc[x.name] , kp0.loc[x.index]))
        phi_pp = phi.apply(lambda x: x / ((kp0.loc[x.name] + kp0.loc[x.index]) / 2 ) )
        np.fill_diagonal(phi_pp.values , 0)
        self._average_proximity = phi_pp
    
    def _calc_average_distance(self):
        """
        Calculate traditional distance (0 is bad , 1 is good distance NOT PROBABILITY)
        to calculate probability you need to substract this value from 1
        """
        density = self._m_cp.dot(self._average_proximity) / self._average_proximity.sum(axis=1)
        self._average_distance = 1 - density

    def _calc_max_prox(self):
        """
        Gets maximum proximity to a product given the basket of products that country currently exports (i.e. m_cp = 1). 
        For example, for combination Country A - Product 1 maximum proximity will be proximity table of Product 1 with products where Country A has m_cp=1. 
        """
        m_cp = self._m_cp.copy()
        m_cp = m_cp.unstack().rename_axis([self._p, self._c]).reset_index(name='m_cp')
        average_proximity = self._average_proximity.copy()
        average_proximity = average_proximity.unstack().rename_axis(['product_1', 'product_2']).reset_index(name='averageBasket_proximity')
        specialization_table = m_cp[m_cp['m_cp'] == 1].groupby(self._p)[self._c].apply(list).reset_index(name='c_list')
        average_proximity = average_proximity.merge(specialization_table, left_on='product_1', right_on=self._p, how='left', validate='m:1')
        max_prox = average_proximity.explode('c_list').groupby(['c_list', 'product_2'], as_index=False)['averageBasket_proximity'].max()
        max_prox = max_prox.rename(columns={'c_list': self._c, 'product_2' : self._p , 'averageBasket_proximity': 'maxProx'})
        self._max_prox = max_prox

    def getMaxProxAndDistance(self, m_cp:pd.DataFrame, average_proximity:pd.DataFrame):
        specialization_table = m_cp[m_cp['m_cp'] == 1].groupby(self._p)[self._c].apply(list).reset_index(name='c_list')
        average_proximity = average_proximity.merge(specialization_table, left_on='product_1', right_on=self._p, how='left', validate='m:1')
        max_prox = average_proximity.explode('c_list').groupby(['c_list', 'product_2'], as_index=False)['averageBasket_proximity'].max()
        max_prox = max_prox.rename(columns={'c_list': self._c, 'product_2' : self._p , 'averageBasket_proximity': 'maxProx'})
        wide_prox = average_proximity.pivot(index='product_1', columns='product_2', values='averageBasket_proximity')
        distance = m_cp.pivot(index=self._c , columns=self._p, values='m_cp').dot(wide_prox) / wide_prox.sum(axis=1)
        distance = 1 - distance
        distance = distance.unstack().reset_index(name='averageProxDistance')
        return max_prox , distance

    def calculate_indexes(self):
        if self.manual == True:
            self._get_diversity()
            self._get_ubiquity()
            self._calc_eci()
            self._calc_pci()
            self._calc_average_proximity()
            self._calc_average_distance()
            self._calc_max_prox()
            self._calc_proximity()
            self._calc_density()
            self._calc_distance()
        else:
            super().calculate_indexes()
    

    @property
    def average_proximity(self):
        return self._average_proximity
    

    @property
    def average_proximity_long(self):
        return self._average_proximity.unstack().rename_axis(['product_1', 'product_2']).reset_index(name='averageBasket_proximity')
    

    @property
    def m_cp_long(self):
        return self._m_cp.unstack().reset_index(name='m_cp')
    

    @property
    def average_proximity_no_duplicates(self):
        f_table = self._average_proximity.unstack().rename_axis(['product_1', 'product_2']).reset_index(name='averageBasket_proximity')
        network = nx.from_pandas_edgelist(f_table, source='product_1', target='product_2' , edge_attr=True)
        return nx.to_pandas_edgelist(network)
    

    @property
    def average_distance(self):
        return self._average_distance

    @property
    def max_prox(self):
        return self._max_prox
    
    @property
    def result_table(self):
        m_cp = self._m_cp.unstack().reset_index(name='m_cp')
        distance = self._average_distance.unstack().reset_index(name='averageDistance')
        max_prox = self._max_prox
        results = pd.merge(m_cp, distance, on=[self._p , self._c] , how='inner', validate='1:1').merge(max_prox , on=[self._p , self._c], how='inner', validate='1:1')
        return results


#data = pd.read_csv('res.csv')
#index = deshtEci(data, c='Country', p='com_class', values='rca_1_net_exp', manual=True )
#index.calculate_indexes()
#index._generate_graphs()
#mx_tr = index._maxst
#econci.edges_nodes_to_csv(mx_tr, 'mx_tree', '.')
