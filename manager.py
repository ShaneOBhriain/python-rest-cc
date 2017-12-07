from flask import Flask, request, jsonify, redirect, url_for, flash
import os, uuid, sys
from werkzeug.utils import secure_filename
from flask import send_from_directory
import requests
import json
import shutil
import git
import time
app = Flask(__name__)

all_commits = []
commit_index = 0
results = []
is_done = False
start_time = False

def test_fn(a,b):
    return a+b

@app.route('/get_work', methods=["GET"])
def get_work():
    global start_time
    if (not start_time):
        start_time = time.time()
    global commit_index
    index_to_return = commit_index
    commit_index = commit_index + 1
    if(commit_index<len(all_commits)):
        return json.dumps({"commit_index":index_to_return})
    else:
        return json.dumps({"error": "No more work."})


@app.route('/get_repository', methods=["GET"])
def get_repository():
    return "https://github.com/rubik/radon"

@app.route('/done', methods=["POST"])
def done():
    print("INSIDE DONE FUNCTION")
    global is_done
    global start_time
    global results
    if (not is_done):
        end_time = time.time()
        time_taken = end_time - start_time
        print("Total time taken: " + str(time_taken))
        is_done = True
        writeResults(results)
    return "Well done worker."

@app.route("/result",methods=["POST"])
def update_results():
    global results
    res = request.form
    cid = res["commit_id"]
    commit = res["commit"]
    complexity = res["complexity"]
    result = {"id":cid,"commit":commit,"complexity":complexity}
    results.append(result)
    return "Successfully updated results"

def writeResults(resultObj):
    print("Writing results")
    with open('results.json', 'w') as outfile:
        json.dump(resultObj, outfile)

def setup():
    REMOTE_URL = get_repository()
    DIR_NAME = "manager-" + str(sys.argv[1])
    if os.path.isdir(DIR_NAME):
        shutil.rmtree(DIR_NAME)
    os.mkdir(DIR_NAME)
    repo = git.Repo.init(DIR_NAME)
    origin = repo.create_remote('origin',REMOTE_URL)
    origin.fetch()
    origin.pull(origin.refs[-1].remote_head)
    global all_commits
    all_commits = list(repo.iter_commits('master'))
    g = git.cmd.Git(DIR_NAME)


if __name__ == '__main__':
    print("Running manager on port " + str(sys.argv[1]))
    setup()
    app.run(host="localhost", port=int(sys.argv[1]))
