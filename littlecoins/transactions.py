#!python3
# coding: utf-8
"""
Place all the .csv files into a DataFrame 
"""

import re
import os
import glob
import numpy as np
import pandas as pd
import sys

def list_of_files(location='.', suffixe='.csv'):
    """Get a list of file names in the current location.

    Parameters
    ----------
    location : str (default local)
        The file location of the files.csv
    suffixe : str (default='.csv')

    Returns
    -------
    list
            list_of_files('.') ->  ['file1.csv', 'file2.csv' , 'file3.csv']
    """
    return [files for files in os.listdir(location) if files.endswith(suffixe)]

# Create a function to process all of the csv files
def read_file_csv(file_csv):
        """read .csv file -> dataframe with columns names added"""
        list_cols = ['City','Acc.','Type','Date','num','Description','Cheque','Expenses','Incomes','NoK1','NoK2','NoK3','NoK4','Cum.']
        df = pd.read_csv(file_csv, header=None, names = list_cols , encoding='latin1')
        return df

def card_debit():
    #Create a list of dataframes
    list_to_concat = [ read_file_csv(df_name)for df_name in list_of_files()]
    df_total = pd.concat(list_to_concat)
    # #Clean the datas
    df_total['Date'] = pd.to_datetime(df_total['Date'], format="%d/%m/%Y" , errors="ignore")
    df_index_by_dates = df_total.set_index(df_total['Date'])
    transactions = df_index_by_dates[['Acc.', 'Date' , 'Description', 'Cheque','Expenses', 'Incomes']]
    transactions = transactions.dropna(how='all')
    transactions.loc[:,'card'] = 'debit'
    return transactions

# ********************************************************

# CC = pd.read_csv("CC_transactions.csv")
def grapping_txt_files_list(location, suffixe='.txt'): # prefixe=None, middle='######'
    """bla bla bla"""
    return [i for i in os.listdir(location) if i.endswith(suffixe)==True]

def scraping_txt_file(filetxt):
    """bla bla bla"""
    datum = []
    with open( filetxt , 'r', encoding='latin1') as foo:
        for line in foo: #I think a genertator is imaginable here!
            pattern = re.compile(
                                r"(?P<Date_de_transaction>\d{2} .{3} \d{4})\t*" \
                                r"(?P<Date_inscription>\d{2} .{3} \d{4})\t*"\
                                r"(?P<Transaction>\d{3})\t{3}"\
                                r"(?P<data4>.*|\s)\t{1}"\
                                r"(?P<Montant>\d{1,4},\d{2})"
                                )
            matchObjects = re.search(pattern, line)
            if matchObjects != None:
                datum.append(matchObjects.groups()) # extract a group of dict
    return datum

def generate_df(file_name , data):
    """bla bla bla"""
    import csv
    csv_name = str(os.path.splitext(file_name)[-2]) + '.csv' # replace .txt - > .csv
    assert type(csv_name) == str, "csv_name : not a string" 
    df = pd.DataFrame(data, columns=['Date','Date_2','number','Description','Expenses'])
    #change the date format of columns 'Date' and delete column 'Date_2'
    calendar = {'JAN':'01' , 'FÉV':'02' , 'MAR':'03' , 'AVR':'04' , 'MAI':'05', 'JUN':'06' , 'JUI':'07' , 'AOÛ':'08' , 'SEP':'09' , 'OCT':'10', 'NOV':'11', 'DÉC':'12'}
    for month,number in calendar.items():
        df['Date'] = df['Date'].str.replace(month,number)         
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d", errors='ignore')
    df = df.drop(['Date_2'], axis=1)
    return df

def card_credit():
    df_list = [generate_df(fname, scraping_txt_file(fname)) for fname in grapping_txt_files_list('.')]
    df_total = pd.concat(df_list)
    REGX = r"^FRAIS.*DE.*CR.*IT"
    frais = df_total[df_total['Description'].str.contains(REGX, regex=True).values]
    frais.loc[frais.Description.str.contains(REGX, regex=True),'Description']= 'credit fees'  
    frais = frais.dropna(how='all')
    frais.loc[:,'card'] = 'credit'
    print(frais.columns)
    transactions = df_total[~df_total['Description'].str.contains(REGX).values]
    transactions = transactions.dropna(how='all')
    transactions.loc[:,'card'] = 'credit' 
    df = pd.concat([transactions,frais])
    df['Expenses'] = df['Expenses'].str.replace(',','.') 
    return 

if __name__ == "__main__":
    total = pd.concat([card_credit(), card_debit()])
    total['Date'] = pd.to_datetime(total['Date']).dt.strftime('%Y-%m-%d')
    total = total.sort_values(by='Date', ascending=False)
    filename = 'total_transactions.csv'
    total.to_csv(filename, index=None)
    print(f"-> {filename} created in the current folder. ")