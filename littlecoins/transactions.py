#!python3
# coding: utf-8

import re
import os
import glob
import numpy as np
import sys
import loguru
import pandas as pd
pd.set_option('mode.chained_assignment', None)

def list_of_files(location="."):
    """return a list of csv files."""
    return [csv for csv in os.listdir(location) if csv.endswith(".csv")]


# Create a function to process all of the csv files
def read_file_csv(file_csv):
    """Read .csv file -> dataframe with columns names added"""
    list_cols = [
        "City",
        "Acc.",
        "Type",
        "date_transaction",
        "num",
        "Description",
        "Cheque",
        "Expenses",
        "Incomes",
        "NoK1",
        "NoK2",
        "NoK3",
        "NoK4",
        "Cum.",
    ]
    df = pd.read_csv(file_csv, header=None, names=list_cols, encoding="latin1")
    return df


def card_debit():
    """Merge all the csv file into one dataframe with all the debit transactions."""
    csv_serie = [read_file_csv(df_name) for df_name in list_of_files()]
    debit = pd.concat(csv_serie, sort=False)
    debit["date_transaction"] = pd.to_datetime(
        debit["date_transaction"], format="%Y/%m/%d", errors="ignore"
    )
    debit = debit.set_index(debit["date_transaction"])
    debit = debit[
        ["Acc.", "date_transaction", "Description", "Cheque", "Expenses", "Incomes"]
    ]
    debit = debit.dropna(how="all")
    debit.loc[:, "card"] = "debit"
    return debit


# ********************************************************

def grapping_txt_files_list(location):
    """Make a list of the text documents in the folder."""
    credit = [txt for txt in os.listdir(location) if txt.endswith(".txt")]
    if not credit:
        return None
    return credit


def scraping_txt_file(filetxt):
    """This scrape the data inside text files using regular expression. """
    datum = []
    with open(filetxt, "r", encoding="latin1") as foo:
        for line in foo:  # I think a genertator is imaginable here!
            pattern = re.compile(
                r"(?P<Date_de_transaction>\d{2}.\w{3}.\d{4})\t*"
                r"(?P<Date_inscription>\d{2}.\w{3}.\d{4})\t*"
                r"(?P<Transaction>\d{3})\t*"
                r"(?P<data4>.*|\s)\t{1}"
                r"(?P<Montant>\d{1,4}[,|.]\d{2})"
            )
            matchObjects = re.search(pattern, line)
            if matchObjects:
                datum.append(matchObjects.groups())  # extract a group of dict
    if not datum:
        return None
    return datum


def generate_df(file_name, data):
    """Generate a dataframe attached to a name."""
    import csv
    df = pd.DataFrame(
        data,
        columns=["date_transaction", "Date_2", "number", "Description", "Expenses"],
    )
    calendar = {
        "JAN": "JAN",
        "FÉV": "FEB",
        "MAR": "MAR",
        "AVR": "APR",
        "MAI": "MAY",
        "JUN": "JUN",
        "JUI": "JUL",
        "AOÛ": "AUG",
        "SEP": "SEP",
        "OCT": "OCT",
        "NOV": "NOV",
        "DÉC": "DEC",
    }
    for month, number in calendar.items():
        df["date_transaction"] = df["date_transaction"].str.replace(month, number)
    df["date_transaction"] = pd.to_datetime(
        df["date_transaction"], format="%d %m %Y", errors="ignore"
    )
    df = df.drop(["Date_2"], axis=1)
    return df


def card_credit():
    df_list = [
        generate_df(fname, scraping_txt_file(fname))
        for fname in grapping_txt_files_list(".")
    ]
    df_total = pd.concat(df_list, sort=False)
    REGX = r"^FRAIS.*DE.*CR.*IT"
    frais = df_total[df_total["Description"].str.contains(REGX, regex=True).values]
    frais.loc[
        frais.Description.str.contains(REGX, regex=True), "Description"
    ] = "credit fees"
    frais = frais.dropna(how="all")
    frais.loc[:, "card"] = "credit"
    transactions = df_total[~df_total["Description"].str.contains(REGX).values]
    transactions = transactions.dropna(how="all")
    transactions.loc[:, "card"] = "credit"
    df = pd.concat([transactions, frais], sort=False)
    df["Expenses"] = df["Expenses"].str.replace(",", ".")
    return df


def main():
    credit, debit = card_credit(), card_debit()
    total = pd.concat([credit, debit], sort=False)
    total["date_transaction"] = pd.to_datetime(total["date_transaction"]).dt.strftime(
        "%Y-%m-%d"
    )
    total = total.sort_values(by='date_transaction', ascending=True) 
    filename = "transactions.csv"
    total.to_csv(filename, index=None)
    print(f"\nReport >>> {filename}")


if __name__ == "__main__":
    main()