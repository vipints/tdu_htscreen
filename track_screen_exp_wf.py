#!/usr/bin/env python
"""
The tracking of screening experiment from multiple steps 

Copyright (C)

2017 - ETH Zuerich, NEXUS Personalized Health Technologies

"""

## standard python libraries
import os 
import sys

import csv 
import pandas 

from collections import defaultdict


def csv_data_loader(file_name):
    """
    load full data from the csv file, returns a dataframe. 

    @args file_name: csv file generated in a screening experiment
    @type file_name: str 
    """

    exp_details = pandas.read_csv(file_name, header=0)
    exp_df = exp_details.fillna(value=0)

    return exp_df 


def barcode_identifier(raw_df):
    """
    extract the source and destination barcodes from a dataframe and returns 
    two lists. 

    @args raw_df: experiment details from csv file
    @type raw_df: pandas dataframe
    """

    ## filter the dataframe columns for barcode information 
    col_names = [] 

    ## general keyword describing the barcode  
    keywords = ["SourceBarcode", "DestinationBarcode"]

    for cols in raw_df: 
        try:
            ## keyword match is exact now and need to replaced with wild 
            ## TODO something like x.str.contains("word")
            if raw_df[cols].apply(lambda x: str(x) in keywords).any():
                col_names.append(cols) 
        except:
            pass 

    #print(col_names)
    ## now the from the selected column, get the barcodes
    src_barcodes = [] 
    dst_barcodes = [] 

    ## selection of barcodes after the matching of keyword 
    for ind_col in col_names:
        ## initializing the flags 
        src_bc_tag = 0 
        dst_bc_tag = 0 
        for element in raw_df[ind_col]:
            if not element:
                ## empty lines are re-initializing the flags 
                src_bc_tag = 0 
                dst_bc_tag = 0 
                continue 
            ## loading the barcode values 
            if src_bc_tag:
                src_barcodes.append(element)  
                continue
            if dst_bc_tag:
                dst_barcodes.append(element)
                continue
            ## checking the barcode types
            if element in "DestinationBarcode":
                dst_bc_tag = 1 
            if element in "SourceBarcode":
                src_bc_tag = 1

    #print src_barcodes
    #print dst_barcodes
    return(src_barcodes, dst_barcodes)


def search_intermediate_files(base_path):
    """
    search for different intermediate files in a screening experiment and 
    returns a list with complete csv and tab files.

    @args base_path: a location where experiment files are stored 
    @type base_path: str
    """

    ## search for the files in a specified path
    csv_tab_files = [] 

    if os.path.isdir(base_path):
        ## walk through the entire base path 
        for root, dirs, files in os.walk(base_path):
            for fname in files: 
                file_prefix, ext = os.path.splitext(fname)
                
                ## selecting files with csv and tab extension  
                #if ext in [".csv", ".tab"]:
                if ext in [".csv"]:
                    tmp_file = os.path.join(root, fname) 
                    csv_tab_files.append(tmp_file)

    return csv_tab_files


def plain_csv_reader(file_name):
    """
    Pandas Error: tokenizing data when dealing with a CSV file that have 
    variable number of columns and read_csv inferred the number of columns
    from the first few rows. To avoid this, use csv module.

    @args file_name: csv file generated in a screening experiment
    @type file_name: str 
    """

    src_barcodes = [] 
    dst_barcodes = [] 
    barcode_flag = 0 

    with open(file_name, "rbU") as csvfile:
        rows = csv.reader(csvfile)
        for line in rows:
            if not line:
                ## resetting the flag variable 
                barcode_flag = 0 
                continue 
            
            try:
                ## FIXME general keyword for searching barcodes
                src_well_ind = line.index("SourceWell")
                src_barcode_ind = line.index("SourceBarcode")
                dst_well_ind = line.index("DestinationWell")
                dst_barcode_ind = line.index("DestinationBarcode")
                barcode_flag = 1 
                continue
            except:
                pass 

            if barcode_flag:
                try:
                    tmp_src = line[src_barcode_ind]
                    tmp_src_well = line[src_well_ind]
                    src_barcodes.append((tmp_src, tmp_src_well))
                except IndexError: 
                    print("error: not able to locate SourceBarcode")
                try:
                    tmp_dst = line[dst_barcode_ind]
                    tmp_dst_well = line[dst_well_ind]
                    dst_barcodes.append((tmp_dst, tmp_dst_well))
                except IndexError: 
                    print("error: not able to locate DestinationBarcode")

    return(src_barcodes, dst_barcodes)


def dfs_search(graph, start, visited=[]):
    """
    method to reduce the experiment direction from the barcodes extracted from
    different intermediate files. 

    @args graph: a dictionary with source and destination barcodes 
    @type graph: defaultdict
    @args start: starting point to infer the path ('ACTITARG-K960PL-1', 'Q1') 
    @type start: tuple 
    """
    
    ##FIXME depends on the well plate 96 or 384 the tracking whole and QX are 
    ## concern to get the right combination

    stack = [start]
    if not visited:
        visited = [start]

    while stack:
        try:
            start = min(list(set(graph[start]) - set(visited)))
            stack.append(start)
            visited.append(start) 
        except: 
            stack.pop()
            if (len(stack) > 0):
                start = stack[-1]
        else:
            node = partial_key_search(graph, start[0])
            for ele in node:
                dfs_search(graph, ele, visited)
    
    return visited


def partial_key_search(brcs, search_key):
    """
    partial match of a tuple key of a dictionary

    @args brcs: a dictionary with source and destination barcodes
    @type brcs: defaultdict
    @args search_key: searching key word, one element of the tuple key 
    @type search_key: str
    """
    ## making key in tuple form
    search_key = (search_key, None) 

    start_vertex = [] 
    for src_wellp, des_wellp in brcs.iteritems():
        if all(xp == xq or xq is None for xp, xq in zip(src_wellp, search_key)):
            start_vertex.append(src_wellp) 

    return start_vertex

## TODO experiment run based on the YAML configuration file
## 1. it is better to have the YAML file for history of experiment search
## 2. minimal input requirement for the executing the experiment

## files and folders associated with multiple screens 
experiment_path = "/Users/vipin/Documents/tdu_screens/"
experiment_path = "/Users/vipin/tmp/track_files"
print('Experiment data imports %s' % experiment_path)

## searh the python dict with similarity key search to identify the right key 
stock_compd_name = "ACTITARG-K960PL-1" 
stock_compd_name = "Drug08_A"

## plate reformatting direction
well_96_to_384 = True
well_384_to_96 = False

## getting all intermediate experiment files from provided path 
exp_files = search_intermediate_files(experiment_path) 
print('Total number of %d file(s) found' % len(exp_files))

## get the barcodes from all files
src_dst_maps = defaultdict(list) 
for asc_file in exp_files:
    ## TODO parsing details about the experiment 
    ## 1. mapping information about the barcode and experiment details

    src_bc, dst_bc = plain_csv_reader(asc_file)
    #print src_bc
    #print dst_bc
    #print 
    ## barcode mapping from source to destination
    try:
        for idx, barcode in enumerate(src_bc):
            src_dst_maps[barcode].append(dst_bc[idx])
    except IndexError:
        print("warning: file %s missing destination barcodes" % asc_file)
        pass 

#print src_dst_maps.keys()
## do the key search to identify the experiment to search
start_node = partial_key_search(src_dst_maps, stock_compd_name) 
#print start_node

## build the graph with extracted barcodes and resolve the experiment path
if start_node:
    for compound in start_node: 
        root = dfs_search(src_dst_maps, compound)
        #print("%s\n%s" % (compound, root))
        for wfsteps in root:
            sys.stdout.write("%s," % wfsteps[0])
        print
else:
    print("error: no stock library %s found" % stock_compd_name)


## TODO the final representation of the experiment flow path 
## 1. visual representation - 
## 2. csv or txt files 
## 3. information about the screen readout file ie, the last element of list root  

## read the formated csv files. This works with pandas 
#csv_df = csv_data_loader(exp_files[0])

## get the barcodes
#src_bc, dst_bc = barcode_identifier(csv_df)

sys.exit(-1)
