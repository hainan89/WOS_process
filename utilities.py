# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 20:54:26 2019

@author: Hainan Chen
@E-mail: hn.chen@live.com
"""

  
def check_paper_citation(paper_a, paper_b):
    '''
    # Check if the two papers have citation relations
    # 0: no citation
    # 1: a to b, b in the citation of a, a->b
    # 2: b to a, a in the citation of b, b->a
    # 3: a and b are cross cited, a<->b
    '''
#    paper_a = paper_df.iloc[0, :]
    try:
        CR_a = paper_a['CR']
        CR_a_list = CR_a.split('\n')
        TI_a = paper_a['TI'].lower()
    except:
        return 0
    
#    paper_b = paper_df.iloc[1, :]
    try:
        CR_b = paper_b['CR']
        CR_b_list = CR_b.split('\n')
        TI_b = paper_b['TI'].lower()
    except:
        return 0
    
    b2a = 0
    for one in CR_b_list:
        if TI_a in one.lower():
            b2a = 1
            break
        
    a2b = 0
    for one in CR_a_list:
        if TI_b in one.lower():
            a2b = 1
            break
    
    # 0: no citation
    # 1: a to b, b in the citation of a, a->b
    # 2: b to a, a in the citation of b, b->a
    # 3: a and b are cross cited, a<->b
    status = b2a * 2 + a2b
    return status
    
def get_author_name_dif(name_a, name_b):
    '''
    # Get the similarity for the given two names
    # return 1, absolutely same name
    # otherwise, return the partition of the same parts
    # to the total parts of the two names
    '''
    if name_a.strip() == name_b.strip():
        # absolutely two same name
        return 1
    else:
        flag = 0
        a_list = name_a.split(" ")
        b_list = name_b.split(" ")
        for n_a in a_list:
            n_a = n_a.replace(",","")
            for n_b in b_list:
                n_b = n_b.replace(",","")
                if n_a == n_b:
                    flag = flag + 1
        # (len of same aprts) / (full len of two names)
        return flag*2/(len(a_list) + len(b_list))
     
def get_paper_authors(AU, AF):
    '''
    # Get the name list for AU and AF
    # AU, Authors; AF, Author Full Name
    '''
    AU_list = [one.strip() for one in AU.split('\n')]
    AF_list = [one.strip() for one in AF.split('\n')]  
    return AU_list, AF_list

if __name__ == "__main__":
    import numpy as np
    import pandas as pd
    
    paper_df = pd.read_csv('./test/paper_df.csv', index_col=0, header=True)
    citation_m = np.zeros((paper_df.shape[0],paper_df.shape[0]))
    for row_i in np.arange(citation_m.shape[0]):
        for col_j in np.arange(row_i, citation_m.shape[0]):
            print(row_i, col_j)
            paper_a = paper_df.iloc[row_i, :]
            paper_b = paper_df.iloc[col_j, :]
            citation_m[row_i, col_j] = check_paper_citation(paper_a, paper_b)
    
    np.savetxt("./test/example-01-citation_m.csv", citation_m, delimiter=',', fmt='%d')

