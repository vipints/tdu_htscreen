#!/usr/bin/env python
"""
The tracking of screening experiment from multiple steps 

Copyright (C)

2017 - ETH Zürich, NEXUS Personalized Health Technologies

"""

import os 
import sys

import pandas 

## this will be the single point of contact for tracking the setup of experiment
## This serve as the source of the experiment start 
 
stock_name = "Kinase"

## The above provided name will be a primary name of the screen 
## Now program need a path to look for the generated folders and files

experiment_path = "/Users/vipin/Documents/tdu_screens/"

## From here on, program aims to search multiple folders to scan intermediate files
## Based on the above mentioned stock name, it will generate the first mapping to the 
## target. From there it will look for the remaining associations. 
## TODO When do the program stop searching for the next association.

## When the program finds a csv it needs to be read
## the module for that here: 

def csv_data_loader(file_name):
	"""
	load full data from the experiment step in a dataframe. 
	
	@args filename: csv file generated in a screening experiment
	@args type: str 
	"""
    
	exp_details = pandas.read_csv(file_name, header=0)
	exp_df = exp_details.fillna(value=0)

	print exp_df.iloc[:,[1,4]]
	## search for the name SourceBarcode and DestinationBarcode from the dataframe selected columns 
 
