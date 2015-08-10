#!/usr/bin/env python

import csv, codecs, cStringIO, datetime
import json
import os
import pause
import requests
import time

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        """Redirect output to a queue"""
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        print row
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_commits(user, repo, api_username, api_password, request_time_log_filename):
    """ Get commit SHA's and messages from a Github repository.

        Arguments:
            user: Github user name of repository
            repo: Name of repository
            api_username: Username for Github API
            api_password: Password for Github API

        Returns:
            List of tuples of the form (user, repo, sha, message)

    """
    request_time_log = open(request_time_log_filename, 'ab')

    start_time = time.time()
    sesh = requests.Session()
    sesh.auth = (api_username, api_password)
    sesh.headers = ({'User-Agent': 'seadeer'})
    url = "https://api.github.com/repos/{user}/{repo}/commits".format(user=user, repo=repo)
    req = sesh.get(url)
    response = req.json()
    messages = parse_response(response)

    elapsed_time = time.time() - start_time
    x_rate_info = get_XRateLimitRemaining(req)
    print "Requests remaining: {x}".format(x=x_rate_info[0])

    request_time_log.write('{time}\n'.format(time=elapsed_time))

    # Go through all the pages of commits data in the repository.
    while True:
        # Check the Github X-Rate limit and wait 
        # if the number of get requests is reaching it.
        x_rate_info = get_XRateLimitRemaining(req)
        print "Requests remaining: {x}".format(x=x_rate_info[0])
        if x_rate_info[0] > 100:
            start_time = time.time()
            if 'next' in req.links.keys():
                url = req.links['next']['url']
                print "Getting link: {url}".format(url=url)
                req = sesh.get(url)
                messages.extend(parse_response(req.json()))
            else:
                break
            elapsed_time = time.time() - start_time
            request_time_log.write('{time}\n'.format(time=elapsed_time))
        else:
            readable_time = datetime.datetime.fromtimestamp((x_rate_info[1]).strftime('%Y-%m-%d %H:%M:%S'))
            pause.until(x_rate_info[1])
            print "Paused until {time}".format(time=readable_time)

    request_time_log.close()
    return [("{}/{}".format(user, repo), sha, message) for (sha, message) in messages]


def parse_response(response):
    """ Extract hashes and commit message strings from API response string. """
    messages = []
    for i in range(len(response)):
        sha = response[i]["sha"]
        message = response[i]["commit"]["message"]
        messages.append((sha, message))
    return messages


def get_XRateLimitRemaining(request):
    """ Get Github XRate information from the response header. """
    remaining = request.headers['X-RateLimit-Remaining']
    reset_time = request.headers['X-RateLimit-Reset']
    return (remaining, reset_time)


def write_csv(msglist, filename):
    """ Save commit messages to CSV file. """
    with open(filename, 'ab') as csv_file:
        writer = UnicodeWriter(csv_file)
        writer.writerows(msglist)


def load_github_config(filename):
    """ Parse a JSON file containing the Github API credentials, returns a dict. """
    with open(filename, 'r') as config_file:
        config = json.load(config_file)

    print config
    return config


def load_repo_list(filename):
    """Getting repository names from a list."""

    # repos = [('pinterest', 'PINRemoteImage'), ('octalmage', 'robotjs')]
    reader = csv.reader(open(filename, 'rb'))
    repos = map(tuple, reader)
    return repos


def main():
    repos = load_repo_list('repo_list.csv')
    config = load_github_config('github_config.json')
    path = "data"
    request_time_log_filename = "request_timing_data.log"

    for (user_name, repo_name) in repos:    
        csv_filename = user_name + '_' + repo_name

        # only download Github data if destination file does not exist
        if os.path.isfile(os.path.join(path, csv_filename)) == False:

            messages = get_commits(user_name, repo_name, config['username'], config['password'], request_time_log_filename)
            csv_filename = os.path.join(path, csv_filename + ".csv")
            write_csv(messages, csv_filename)
            message_count = len(messages)
            print "Downloaded {user_name}/{repo_name} to {csv_filename}, {message_count} messages added.".format(**locals())


if __name__ == '__main__':
    main()

