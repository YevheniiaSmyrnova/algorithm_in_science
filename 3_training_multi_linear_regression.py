"""
Training multi-linear regression
"""
import pandas as pd
import pickle
import random
from neo4j.v1 import GraphDatabase, basic_auth
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingRegressor

# Connect to database
db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

# Work with database
with driver.session() as session:
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")
        
    with session.begin_transaction() as create_customers:
        create_customers.run(
            """FOREACH(customer IN range(1,20) | 
            CREATE (:Customer {country_id: round(rand()*100+1), age: round(rand()*18+18)}))""")

    with session.begin_transaction() as create_companies:
        create_companies.run(
            """FOREACH(company IN range(1,10) | 
            CREATE (:Company {country_id: round(rand()*100+1), customers_daily: round(rand()*10)+1}))""")
        
    with session.begin_transaction() as add_relationships:
        add_relationships.run(
            """MATCH (customer :Customer), (company :Company) 
            WHERE customer.country_id < company.country_id AND NOT (customer)-[:BUYING_IN]->(company) 
            CREATE (customer)-[bi :BUYING_IN]->(company) 
            SET bi.game=round(rand()*2)+1, bi.web_application=round(rand()*10)+1, 
            bi.mobile_application=round(rand()*8)+1""")
        
    with session.begin_transaction() as get_data:
        result = get_data.run(
            """MATCH (customer :Customer)-[bi :BUYING_IN]->(company :Company)
            RETURN customer.country_id as customer_country_id, customer.age as customer_age,
            company.country_id as company_country_id, company.customers_daily as customers_daily,
            bi.game as game, bi.web_application as web_application, bi.mobile_application as mobile_application""")
        training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

print "Test data set information:"
print training_data.info()

# Make test data set
# X_data - matrix with features columns
# Y_data - matrix with responses columns
features_columns = [x for x in training_data.columns if x not in ['game', 'web_application', 'mobile_application']]
responses_columns = ['game', 'web_application', 'mobile_application']
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

print X_data.head()
print Y_data.head()

# Work with sklearn
model = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(X_data, Y_data)

# New data set and predict
new_data = pd.DataFrame(data={'customer_country_id': [random.randint(0, 300), random.randint(0, 300), random.randint(0, 300)],
                              'customer_age': [random.randint(0, 80), random.randint(0, 80), random.randint(0, 80)],
                              'company_country_id': [random.randint(0, 300), random.randint(0, 300), random.randint(0, 300)],
                              'customer_daily': [random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)]})
print "New data set:"
print new_data

output = model.predict(new_data).round()
output_data = pd.DataFrame({'game': output[:, 0], 'web_application': output[:, 1], 'mobile_application': output[:, 2]})
print "Our prediction:"
print output_data

# Save and load model
model_pkl_filename = 'prediction_model.pkl'
with open(model_pkl_filename, 'wb') as pickled_model:
    pickle.dump(model, pickled_model)

with open(model_pkl_filename, 'rb') as model_pkl:
    prediction_model = pickle.load(model_pkl)

new_data = pd.DataFrame(data={'customer_country_id': [random.randint(0, 300)],
                              'customer_age': [random.randint(0, 80)],
                              'company_country_id': [random.randint(0, 300)],
                              'customer_daily': [random.randint(0, 50)]})
print "New data set 2:"
print new_data

output = prediction_model.predict(new_data).round()
output_data = pd.DataFrame({'game': output[:, 0], 'web_application': output[:, 1], 'mobile_application': output[:, 2]})
print "Our prediction:"
print output_data
