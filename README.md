# Algorithm in science

## Prerequisites:
* `python2.7` is required.
* `ipython`, `ipython-notebook` and `Jupyter`are needed for running. Here are the instructions:

https://www.digitalocean.com/community/tutorials/how-to-set-up-a-jupyter-notebook-to-run-ipython-on-ubuntu-16-04

* `neo4j` is needed for running. Here are the instructions:

https://neo4j.com/docs/operations-manual/current/installation/linux/debian/?_ga=2.249168388.2041192375.1507250087-893468657.1507250087

Then
```
sudo rm /var/lib/neo4j/data/dbms/auth
sudo neo4j-admin set-default-admin neo4j
sudo neo4j-admin set-initial-password 12345qwert
```

## Usage

To run neo4j locally make the next steps:
```
sudo service neo4j start
```
Go to `http://0.0.0.0:7474/browser/`

To run jupyter locally make the next steps:
```
jupyter notebook
```
Go to `http://localhost:8888/tree`.

To run script make the next steps:
```
git clone https://github.com/YevheniiaSmyrnova/algorithm_in_science.git
cd algorithm_in_science/
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
python 1_training_logistic_regression.py
```
