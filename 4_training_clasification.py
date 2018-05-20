"""
Training clasification
"""
import pandas as pd
import pickle
import random
from neo4j.v1 import GraphDatabase, basic_auth
from sklearn import tree

# Connect to database
db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

# Work with database
with driver.session() as session:
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")

    with session.begin_transaction() as add_projects:
        add_projects.run(
            """FOREACH(project IN range(1,20) |
            CREATE (:Project {duration: round(rand()*180+30), budget: round(rand()*1000*16+1000),
            team: round(rand()*15+1), customer_id: round(rand()*10+1)}))""")
        
    with session.begin_transaction() as add_classes:
        add_classes.run(
            """MATCH (project :Project)
            WITH project, [1, 2, 3] as classes, toInt(round(rand()*10)%3) as type
            WITH project, classes, type, classes[type] as class
            SET project.class = class """)

    # get data from database
    with session.begin_transaction() as get_data:
        result = get_data.run(
            """MATCH (project :Project)
            RETURN project.duration as duration, project.budget as budget,
            project.team as team, project.customer_id as customer_id, project.class as class""")
        training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

print "Test data set information:"
print training_data.info()

# Make test data set
# X_data - matrix with features columns
# Y_data - matrix with responses columns
features_columns = [x for x in training_data.columns if x not in ["class"]]
responses_columns = ["class"]
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

print X_data.head()
print Y_data.head()

# Work with sklearn
model = tree.DecisionTreeClassifier().fit(X_data, Y_data)

# New data set and predict
new_data = pd.DataFrame(data={"duration": [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)],
                              "budget": [random.randint(0, 100000), random.randint(0, 100000), random.randint(0, 100000)],
                              "team": [random.randint(0, 20), random.randint(0, 20), random.randint(0, 20)],
                              "customer_id": [random.randint(0, 15), random.randint(0, 15), random.randint(0, 15)]})
print "New data set:"
print new_data

output = model.predict(new_data)
output_data = pd.DataFrame({"class": output})
print "Our prediction:"
print output_data

# Save and load model
model_pkl_filename = "prediction_model.pkl"
with open(model_pkl_filename, "wb") as pickled_model:
    pickle.dump(model, pickled_model)

with open(model_pkl_filename, "rb") as model_pkl:
    prediction_model = pickle.load(model_pkl)

new_data = pd.DataFrame(data={"duration": [random.randint(0, 100)],
                              "budget": [random.randint(0, 100000)],
                              "team": [random.randint(0, 20)],
                              "customer_id": [random.randint(0, 15)]})
print "New data set 2:"
print new_data

output = prediction_model.predict(new_data)

output_data = pd.DataFrame({"class": output})
print "Our prediction:"
print output_data
