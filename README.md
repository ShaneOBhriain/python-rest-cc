# python-rest-cc
Python REST example for distributed calculation of cyclomatic complexity 

Manager node is a Flask API with /get_work endpoint for workers to request work, as well as /result for submission of results.

The distribution of work is based on a Work Stealing pattern.

The workers ask for work, and receive a commit_id which they can check out and calculate the cyclometic complexity of files relevant to that commit.
If no more work is available, the worker will sleep for two seconds and try again, to allow for the addition of work by the manager.
After three rejections, the work process will stop and send a "done" message to the manager.



