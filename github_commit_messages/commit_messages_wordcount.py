#!/usr/bin/env python

""" Count the words per commit in each repository.

    Input: CSV file, each line containing user_name, repo_name, commit_hash, commit_message.

    Output: CSV file, each line contains the singe value word_count(commit_message).
"""

from nltk.tokenize import RegexpTokenizer
import csv, os

def import_csv(filename):
    path = "data"
    messages_list = []
    reader = csv.reader(open(os.path.join(path, filename), 'rb'))
    for row in reader:
        print filename
        print row
        messages_list.append(row[2])
    return messages_list

def get_word_count(filename):
    messages_list = import_csv(filename)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = [len(tokenizer.tokenize(message)) for message in messages_list]
    return tokens

def get_word_count_all(path):
    for csv_file in os.listdir(path):
        if not csv_file.endswith('.csv'):
            continue
        tokens = get_word_count(csv_file)
        with open ('token_file.csv', 'ab') as tokenfile:
            writer = csv.writer(tokenfile)
            writer.writerow([csv_file, tokens])
            tokenfile.close()


def main():
    get_word_count_all('./data/')


if __name__ == '__main__':
    main()
