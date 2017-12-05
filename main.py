from radon.complexity import cc_visit
import git
import os
import shutil
import time

def fileComplexity(filename):
    with open(filename) as fobj:
        results = cc_visit(fobj.read())
        totalComplexity = sum([i.complexity for i in results])
    return totalComplexity

def main():
    DIR_NAME = "temp"
    REMOTE_URL = "https://github.com/rubik/radon"
    if os.path.isdir(DIR_NAME):
        shutil.rmtree(DIR_NAME)
    os.mkdir(DIR_NAME)
    repo = git.Repo.init(DIR_NAME)
    origin = repo.create_remote('origin',REMOTE_URL)
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    print(origin.refs[0].remote_head)
    all_commits = list(repo.iter_commits('master', skip=20))
    # tree = repo.heads.master.commit.tree

    g = git.cmd.Git(DIR_NAME)
    allComplexities = []
    print ("---- DONE ----")
    print("Number of commits: " + str(len(all_commits)))
    start_time = time.time()
    for commit in all_commits:
        commitComplexities = []
        print("------------- Commit -----------------")
        print(commit)
        print("--------------------------------------")
        g.checkout(commit)
        for blob in list(commit.tree.traverse()):                                         # intuitive iteration of tree members
                if blob.path[-3:] == ".py":
                    try:
                        complexity = fileComplexity("temp/" + blob.path)
                        commitComplexities.append(complexity)
                    except:
                        print("Error with file : " + blob.path)
        totalCommitComplexity = sum(commitComplexities)
        print("Complexity of commit: " + str(totalCommitComplexity))
        allComplexities.append(totalCommitComplexity)
    print(allComplexities)
    print(str(len(allComplexities)))
    # blob = tree.trees[0].blobs[0]                              # let's get a blob in a sub-tree
    # print(blob.name + " : " + blob.path)
    time_taken = time.time() - start_time
    print("Time taken: " + str(time_taken))



main()
