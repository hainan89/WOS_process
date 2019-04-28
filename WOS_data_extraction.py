# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 18:31:14 2019

@author: Hainan Chen
@E-mail: hn.chen@live.com
"""
import re
import numpy as np
import pandas as pd
from itertools import combinations

from utilities import get_paper_authors
'''
# Get literature paper information items.
# Designed for the Web of Science exported txt data.
'''

def get_paper_list(fpath):
    '''
    # Get paper list with the given wos txt file path
    # fpath = './test/example-01.txt'
    '''
    with open(fpath, encoding='utf8') as f:
        lines = f.readlines()
        
        paper_list = []
        temp_one_paper = []
        for one in lines:
            if re.match(r"PT\s{1}[A-Z]{1}", one):
                # start of one paper
                temp_one_paper = []
            elif re.match(r"ER\n", one):
                # end of one paper
                temp_one_paper.append(one)
                paper_list.append("".join(temp_one_paper))
            temp_one_paper.append(one)
    return paper_list

def get_one_paper_items(paper_str):
    '''
    # Get information items of one given paper
    # translate into dict
    # paper_str: one paper data with string format
    '''
    paper_str_lines = paper_str.split('\n')
    
    line_i = 0
    paper_dict = {}
    previous_item = None
    is_previous = False
    temp_item_val = []
    while(line_i < len(paper_str_lines)):
        current_line = paper_str_lines[line_i]
        # if first two letters are not blank, it is one item
        current_item = current_line[0:2].strip()
        if len(current_item) > 0:
            if is_previous is True:
                # save one continous item into one str
                temp_item_val = np.concatenate([[paper_dict[previous_item]], 
                                                temp_item_val])
                paper_dict[previous_item] = "\n".join(temp_item_val)
                is_previous = False
                
            paper_dict[current_item] = current_line[3:].strip()
            previous_item = current_item
            temp_item_val = []
        else:
            # following the previous item
            temp_item_val.append(current_line[3:].strip())
            is_previous = True
            
        line_i = line_i + 1
    
    return paper_dict

def get_one_paper_references(paper_dict, paper_ID = 0):
    '''
    # Get the references data with one given paper record
    # input: paper_dict, dict format, paper_ID, int
    # return: list of reference dicts
    # return [{Author, Year, Source, Vol, Page, Paper ID}]
    '''
    ref_list = []
    try:
        CR_a = paper_dict['CR']
        CR_a_list = CR_a.split('\n')
    except:
        return ref_list
    
    for one in CR_a_list:
        ref_items = one.split(',')
        if len(ref_items) != 5:
            continue 
        ref_item_dict = {}
        ref_item_dict['Author'] = ref_items[0].strip()
        ref_item_dict['Year'] = ref_items[1].strip()
        ref_item_dict['Source'] = ref_items[2].strip()
        ref_item_dict['Vol'] = ref_items[3].replace('V', '').strip()
        ref_item_dict['Page'] = ref_items[4].replace('P', '').strip()
        ref_item_dict['Paper ID'] = paper_ID
        ref_list.append(ref_item_dict)
    return ref_list

def get_paper_citation_records(paper_list, is_save=True, save_folder='./test'):
    '''
    # get the dict format of all paper record
    # get the list of dict of all paper references
    # input: paper_list, string list formated paper data
    # output: paper_df, DataFrame formated all paper reocrd
    #         paper_ref_dict_df, DataFrame formated all paper reference record
    '''
    paper_dict_list = []
    paper_ref_dict_list = []
    paper_ID = 0
    for one in paper_list:
        one_paper_dict = get_one_paper_items(one)
        
        paper_dict_list.append(one_paper_dict)
        
        one_paper_ref_list = get_one_paper_references(one_paper_dict, paper_ID)
        paper_ref_dict_list = np.concatenate([paper_ref_dict_list, one_paper_ref_list])
        
        paper_ID = paper_ID + 1
        print('paper_ID:', paper_ID)
    
    # save to csv file
    paper_df = pd.DataFrame(paper_dict_list)
    
    # save to csv file
    paper_ref_dict_df = pd.DataFrame(list(paper_ref_dict_list))
    paper_ref_dict_df = paper_ref_dict_df[['Paper ID', 'Author','Year','Source',
                                           'Vol','Page']]
    
    if is_save == True:
        paper_df.to_csv('{0}/paper_df.csv'.format(save_folder), 
                        index=True, header=True)
        paper_ref_dict_df.to_csv('{0}/paper_ref_df.csv'.format(save_folder), 
                                 index=True, header=True)
    
    return paper_df, paper_ref_dict_df

def get_paper_citation_matrix(paper_df, paper_ref_dict_df, is_save=True, 
                                 save_folder='./test'):
    '''
    # Get the citation matrix for the paper_df records
    # return citation_m with shape of (paper_df.shape[0] x paper_df.shape[0])
    # row -> col, 1 means row is one reference of col
    # the row and col are the index of the paper record in paper_df
    '''
    Author = np.array([one.upper() for one in paper_ref_dict_df['Author']])
    Source = np.array([one.upper() for one in paper_ref_dict_df['Source']])
    
    citation_m = np.zeros((paper_df.shape[0],paper_df.shape[0]))
    
    for paper_i in np.arange(paper_df.shape[0]):
        AU = paper_df.loc[paper_i,'AU']
        AF = paper_df.loc[paper_i, 'AF']
        AU_list, AF_list = get_paper_authors(AU, AF)
        Year = paper_df.loc[paper_i, 'PY']
        VL = paper_df.loc[paper_i, 'VL']
        Page = "{0}-{1}".format(paper_df.loc[paper_i, 'BP'], 
                paper_df.loc[paper_i, 'EP'])
        SO = paper_df.loc[paper_i, 'SO']
        
        m_AU = Author == AU_list[0].upper().replace(',','')
        m_AF = Author == AF_list[0].upper().replace(',','')
        m_Year = paper_ref_dict_df['Year'] == Year
        m_SO = Source == SO.upper()
        m_VL = paper_ref_dict_df['Vol'] == VL
        m_Page = paper_ref_dict_df['Page'] == Page
        
        mask = (m_AU | m_AF) & m_Year & m_SO & m_VL & m_Page
        to_paper_ids = paper_ref_dict_df.loc[mask, 'Paper ID']
        to_paper_ids = list(set(to_paper_ids))
        
        citation_m[paper_i, to_paper_ids] = 1
        
        print('paper_i', paper_i)
    
    citation_m_df = pd.DataFrame(citation_m)
    if is_save == True:
        citation_m_df.to_csv('citation_m_df.csv',index=True, header=True)
        
    return citation_m

def get_paper_co_citation_matrix(paper_df, paper_ref_dict_df, is_save=True, 
                                 save_folder='./test'):
    '''
    # Get the co-citation records for papers
    # input: paper_df is the dict formated paper records
    # input: paper_ref_dict_df is the references records for all the papers
    # return: citation_m stored the count of the co-cited references
    '''
    
    # test variable
    to_paper_ids_list = []
    
    citation_m = np.zeros((paper_df.shape[0],paper_df.shape[0]))
    
    # To uppercases to make sure to have the same situations
    Author = np.array([one.upper() for one in paper_ref_dict_df['Author']])
    Source = np.array([one.upper() for one in paper_ref_dict_df['Source']])
    
    ref_list = ["{0}{1}{2}{3}{4}".format(one[1]['Author'].upper(), 
                                        one[1]['Year'],
                                        one[1]['Source'].upper(), 
                                        one[1]['Vol'], 
                                        one[1]['Page']) for one in paper_ref_dict_df.iterrows()]
    ref_list = np.array(ref_list)
    
    for ref_i in np.arange(paper_ref_dict_df.shape[0]):
        author = Author[ref_i]
        year = paper_ref_dict_df.loc[ref_i, 'Year']
        source = Source[ref_i]
        vol = paper_ref_dict_df.loc[ref_i, 'Vol']
        page = paper_ref_dict_df.loc[ref_i, 'Page']
        
        target = "{0}{1}{2}{3}{4}".format(author, year, source, vol, page)
        
        mask = ref_list == target
        
        to_paper_ids = paper_ref_dict_df.loc[mask, 'Paper ID']
        to_paper_ids = list(set(to_paper_ids))
        
        to_paper_ids_list.append(to_paper_ids)
        
        print(ref_i, len(to_paper_ids))
        if len(to_paper_ids) > 1:
            combs = combinations(to_paper_ids, 2)    
            for one in combs:
                citation_m[one[0], one[1]] = citation_m[one[0], one[1]] + 1
    
    co_citation_m_df = pd.DataFrame(citation_m)    
    if is_save == True:
        co_citation_m_df.to_csv('{0}/co_citation_m_df.csv'.format(save_folder), 
                        index=True, header=True)
    return citation_m
    
if __name__ == "__main__":
    
    # get the string format of each paper record
    fpath = './test/example-01.txt'
    paper_list = get_paper_list(fpath)
    
    paper_df, paper_ref_dict_df = get_paper_citation_records(paper_list)
    
    test = pd.read_csv('./test/paper_ref_df.csv', index_col=0, header=0)
    
    
    
    
    