import git
import os
import shutil
import time
import dispy
import json

def fileComplexity(commit,filename,theFile):
    from radon.complexity import cc_visit
    results = cc_visit(theFile)
    complexity = sum([i.complexity for i in results])
    return (commit,filename,complexity)

def writeResults(resultObj):
    with open('results.json', 'w') as outfile:
        json.dump(resultObj, outfile)

def main():
    DIR_NAME = "temp"
    REMOTE_URL = "https://github.com/rubik/radon"
    if os.path.isdir(DIR_NAME):
        shutil.rmtree(DIR_NAME)
    os.mkdir(DIR_NAME)
    repo = git.Repo.init(DIR_NAME)
    origin = repo.create_remote('origin',REMOTE_URL)
    origin.fetch()
    origin.pull(origin.refs[-1].remote_head)
    all_commits = list(repo.iter_commits('master'))
    g = git.cmd.Git(DIR_NAME)
    allComplexities = {}
    print ("Successfully pulled repository.")

    cluster = dispy.JobCluster(fileComplexity)
    jobs = []

    for commit in all_commits:
        commitComplexities = []
        allComplexities[str(commit)] = {}
        g.checkout(commit)
        for blob in list(commit.tree.traverse()):                                         # intuitive iteration of tree members
                if blob.path[-3:] == ".py":
                    try:
                        filename = "temp/" + blob.path
                        with open(filename) as fobj:
                            theFile = fobj.read()
                            job = cluster.submit(str(commit),blob.path,theFile)
                            jobs.append(job)
                    except:
                        print("Error with file : " + blob.path)

    start_time = time.time()
    for job in jobs:
        try:
            commit, filename, complexity = job() # waits for job to finish and returns results
            allComplexities[commit][filename] = complexity
        except TypeError:
            print("Type Error")

    time_taken = time.time() - start_time
    writeResults(allComplexities)
    print("Done")
    print("Time taken to analyze "+ (str(len(allComplexities)))+" commits: " + str(time_taken))

main()
