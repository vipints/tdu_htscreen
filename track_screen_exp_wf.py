#!/usr/bin/env python
"""
The tracking of screening experiment from multiple steps 

Copyright (C)

2017 - ETH Zuerich, NEXUS Personalized Health Technologies

"""

## standard python libraries
import os 
import sys

import pandas 

## this will be the single point of contact for tracking the setup of experiment
## This serve as the source of the experiment start 
 
stock_name = "Kinase"

## The above provided name will be a primary name of the screen 
## Now program need a path to look for the generated folders and files

experiment_path = "/Users/vipin/Documents/tdu_screens/"

intermediate_file = "%s/exp-setup/VI000821.tab.csv" % experiment_path
## From here on, program aims to search multiple folders to scan intermediate files
## Based on the above mentioned stock name, it will generate the first mapping to the 
## target. From there it will look for the remaining associations. 
## TODO When do the program stop searching for the next association.

## When the program finds a csv it needs to be read
## the module for that here: 

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


## read the file
csv_df = csv_data_loader(intermediate_file)

## get the barcodes
src_bc, dst_bc = barcode_identifier(csv_df)

## TODO search for the files in a specified path
## csv or tab 

print src_bc 
print dst_bc

sys.exit(-1)
