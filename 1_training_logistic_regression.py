from neo4j.v1 import GraphDatabase, basic_auth
import pandas as pd

from sklearn.linear_model import LogisticRegression

# ----- connection -------

db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

with driver.session() as session:
    # erase database
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")

    # add users with properties score_math up to 10 and score_English up to 10
    with session.begin_transaction() as create_users:
        create_users.run("FOREACH(r IN range(1,10)| "
                         "CREATE (u :User {user_id: r, score_math: rand()*10, score_English: rand()*10}))")

        # add random relationships between users
    with session.begin_transaction() as add_relationships:
        add_relationships.run("MATCH(user_1 :User), (user_2 :User) "
                              "WHERE rand()<0.3 AND NOT user_1.user_id=user_2.user_id "
                              "CREATE(user_1)-[:INTERESTED_IN]->(user_2)")
with driver.session() as session:
    # get vectors with data from database
    with session.begin_transaction() as get_data:
        result = get_data.run(
            "MATCH(user_1 :User), (user_2 :User) "
            "WHERE NOT user_1.user_id=user_2.user_id "
            "WITH user_1.user_id as interested_user_id, user_2.user_id as user_id, "
            "user_1.score_math as interested_score_math, user_2.score_math as user_score_math, "
            "user_1.score_English as interested_score_English, user_2.score_English as user_score_English, "
            "CASE WHEN (user_1)-[:INTERESTED_IN]->(user_2) THEN 1 ELSE 0 END as interested_in "
            "RETURN interested_user_id, user_id, interested_score_math, user_score_math, interested_score_English, user_score_English, interested_in "
        )
        training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

print training_data
print training_data.info()

# create 2 variables called X_data and Y_data:
# X_data shall be a matrix with features columns
# and Y_data shall be a matrix with responses columns

features_columns = [x for x in training_data.columns if x not in ['interested_user_id','user_id', 'interested_in']]
responses_columns = ['interested_in']
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

print X_data.head()

print Y_data

y = Y_data["interested_in"].values

print y

# import Logistic Regression

# give a name to Logistic regression model
model_1 = LogisticRegression()

# put our data to train model
model_1.fit(X_data, y)

# create new data

new_data = pd.DataFrame(data = {'interested_score_English': [9.3, 8.2, 0.1], 'interested_score_math': [0.45, 4.6, 8.3], 'user_score_English': [2.7, 4.2, 5.3], 'user_score_math': [7.4, 6.5, 5.4]})

print new_data

# predict a value of getting values 0 or 1
print model_1.predict(new_data)

# predict probability of getting value 1 (we will have probabilities of getting 0 an 1, we need 1)
print model_1.predict_proba(new_data)[:, 1]

output = model_1.predict_proba(new_data)[:, 1]

output_data = pd.DataFrame({'interested_in': output})

print output_data
