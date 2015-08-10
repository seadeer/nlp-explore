#!/usr/bin/env python

""" Count the words per commit in each repository.

    Input: CSV file, each line containing user_name, repo_name, commit_hash, commit_message.

    Output: CSV file, each line contains the singe value word_count(commit_message).
"""

from nltk.tokenize import RegexpTokenizer
import csv, os

def import_csv(filename):
    """Gets Github commit messages from a csv file and returns them as a list."""
    path = "data"
    messages_list = []
    reader = csv.reader(open(os.path.join(path, filename), 'rb'))
    for row in reader:
        print filename
        print row
        messages_list.append(row[2])
    return messages_list

def get_word_count(filename):
    """
    Does word counts of each commit message 
    in the file and returns them as a list.
    """
    messages_list = import_csv(filename)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = [len(tokenizer.tokenize(message)) for message in messages_list]
    return tokens

def get_word_count_all(path):
    """
    Goes through all the csv files in the path
    and saves word count for each file.
    """
    for csv_file in os.listdir(path):
        if not csv_file.endswith('.csv') or csv_file.startswith('wordcount'):
            continue
        tokens = get_word_count(csv_file)
        filename = 'wordcount_{filename}'.format(filename=csv_file)
        with open(os.path.join(path, filename), 'wb') as count_file:
            count_file.writelines(str(token)+'\n' for token in tokens)


def main():
    get_word_count_all('./data/')


if __name__ == '__main__':
    main()
