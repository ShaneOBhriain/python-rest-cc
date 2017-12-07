from flask import Flask, request
import requests
import sys
import git
import shutil
import os
from radon.complexity import cc_visit
import time

DIR_NAME = ""
all_commits = []
g = ""
repo = ""

def fileComplexity(theFile):
    results = cc_visit(theFile)
    complexity = sum([i.complexity for i in results])
    return complexity

def get_repository_url():
    res = requests.get("http://localhost:8001/get_repository")
    url = res.text
    return url

def getCommitComplexity(commit):
    file_complexities = []
    g.checkout(commit)
    for blob in list(commit.tree.traverse()):
        if blob.path[-3:] == ".py":
            filename = DIR_NAME + "/"+blob.path
            try:
                with open(filename) as fobj:
                    theFile = fobj.read()
                    fc = fileComplexity(theFile)
                    file_complexities.append(fc)
            except:
                print("")
    total_commit_complexity = sum(file_complexities)
    return total_commit_complexity


def setup():
    REMOTE_URL = get_repository_url()
    global DIR_NAME
    DIR_NAME = "worker-" + str(sys.argv[1])
    if os.path.isdir(DIR_NAME):
        shutil.rmtree(DIR_NAME)
    os.mkdir(DIR_NAME)
    repo = git.Repo.init(DIR_NAME)
    origin = repo.create_remote('origin',REMOTE_URL)
    origin.fetch()
    origin.pull(origin.refs[-1].remote_head)
    global all_commits
    global g
    all_commits = list(repo.iter_commits('master'))
    print("length of list " + str(len(list(repo.iter_commits('master')))))
    g = git.cmd.Git(DIR_NAME)

def main():
    print("Running worker on port " + str(sys.argv[1]))
    setup()
    rejected_count = 0
    while rejected_count<3:
        res = requests.get("http://localhost:8001/get_work")
        try:
            commit_index = res.json()["commit_index"]
            commit_to_check = all_commits[commit_index]
            complexity = getCommitComplexity(commit_to_check)
            msg = {"commit_id": commit_index, "commit":str(commit_to_check), "complexity": complexity}
            requests.post("http://localhost:8001/result", data=msg)
        except KeyError:
            rejected_count = rejected_count +1
            time.sleep(2)

    requests.post("http://localhost:8001/done")
    print("Rejected after asking for work 3 times. Killing worker.")

main()
