"""
Training logistic regression
"""
import pandas as pd
import random
from neo4j.v1 import GraphDatabase, basic_auth
from sklearn.linear_model import LogisticRegression

# Connect to database
db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

# Work with database
with driver.session() as session:
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")

    with session.begin_transaction() as create_developers:
        create_developers.run(
            "FOREACH(r IN range(1,10)| "
            "CREATE (u :Developer {developer_id: r, django_knowledge: rand()*10, angular_knowledge: rand()*10}))")

    with session.begin_transaction() as add_relationships:
        add_relationships.run(
            "MATCH(developer_1 :Developer), (developer_2 :Developer) "
            "WHERE rand()<0.3 AND NOT developer_1.developer_id=developer_2.developer_id "
            "CREATE(developer_1)-[:NEEDS_HELD]->(developer_2)")

    with session.begin_transaction() as get_data:
        result = get_data.run(
            "MATCH(developer_1 :Developer), (developer_2 :Developer) "
            "WHERE NOT developer_1.developer_id=developer_2.developer_id "
            "WITH developer_1.developer_id as developer_needs_help, "
            "developer_2.developer_id as developer, "
            "developer_1.django_knowledge as needed_django_knowledge, "
            "developer_2.django_knowledge as django_knowledge, "
            "developer_1.angular_knowledge as needed_angular_knowledge, "
            "developer_2.angular_knowledge as angular_knowledge, "
            "CASE WHEN (developer_1)-[:NEEDS_HELD]->(developer_2) THEN 1 ELSE 0 END as needs_help "
            "RETURN developer_needs_help, developer, needed_django_knowledge, django_knowledge, "
            "needed_angular_knowledge, angular_knowledge, needs_help "
        )
        training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])
print "Test data set information"
print training_data.info()

# Make test data set
# X_data - matrix with features columns
# Y_data - matrix with responses columns
features_columns = [x for x in training_data.columns if x not in ['developer_needs_help', 'developer', 'needs_help']]
responses_columns = ['needs_help']
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

y = Y_data["needs_help"].values

# Work with sklearn
model = LogisticRegression()
model.fit(X_data, y)

# New data set and predict
new_data = pd.DataFrame(data={'needed_django_knowledge': [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)],
                              'needed_angular_knowledge': [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)],
                              'django_knowledge': [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)],
                              'angular_knowledge': [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)]})
model.predict(new_data)
output = model.predict_proba(new_data)[:, 1]
output_data = pd.DataFrame({'needs_help': output})
print "Our prediction:"
print output_data
