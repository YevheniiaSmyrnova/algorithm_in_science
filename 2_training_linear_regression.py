"""
Training linear regression
"""
import pandas as pd
import pickle
import random
from neo4j.v1 import GraphDatabase, basic_auth
from sklearn.linear_model import LinearRegression

# Connect to database
db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

# Work with database
with driver.session() as session:
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")

    with session.begin_transaction() as create_orders:
        create_orders.run(
            """FOREACH(r IN range(0,10) |
            CREATE (p :Order {order_id: r}))""")

    with session.begin_transaction() as create_products:
        create_products.run(
            """MATCH (order :Order)
            FOREACH(r IN range(1,10) |
            CREATE (p :Product {order_id: r, price: rand()*10})-[:BELONGS_TO]->(order))""")

    with session.begin_transaction() as create_customers:
        create_customers.run(
            """WITH ["Alex", "Gordon", "Robert", "Leonardo", "Paul"] AS name
            FOREACH (i IN range(1,20) |
            CREATE (c :Customer {customer_id: i, FirstName: name[i % size(name)], income: rand()*5, cooperation_duration: rand()*10}))""")

    for i in range(1, 30):
        with session.begin_transaction() as create_buy_transaction:
            create_buy_transaction.run(
                """MATCH (customer :Customer), (order :Order), (product :Product)
                WHERE customer.income > product.price
                MERGE(customer)-[:BUY]->(product)""")

        with session.begin_transaction() as get_data:
            result = get_data.run(
                """MATCH(customer :Customer)-[buy :BUY]-(product :Product)-[:BELONGS_TO]->(:Order)
                WITH customer.customer_id as customer_id,
                customer.FirstName as name,
                customer.income as income,
                customer.cooperation_duration as cooperation_duration,
                COUNT(buy) as transaction
                RETURN customer_id, name, income, cooperation_duration, transaction""")
            training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

print "Test data set information:"
print training_data.info()


# Make test data set
# X_data - matrix with features columns
# Y_data - matrix with responses columns
features_columns = [x for x in training_data.columns if x not in ["customer_id", "name", "transaction"]]
responses_columns = ["transaction"]
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

y = Y_data["transaction"].values


# Work with sklearn
model = LinearRegression()
model.fit(X_data, y)

# New data set and predict
new_data = pd.DataFrame(data={"income": [random.randint(1, 5), random.randint(1, 5), random.randint(1, 5)],
                              "cooperation_duration": [random.randint(0, 10), random.randint(0, 10), random.randint(0, 10)]})
print "New data set 1:"
print new_data

output = model.predict(new_data)
output_data = pd.DataFrame({"transaction": output.round()})
print "Our prediction:"
print output_data

# Save and load model
model_filename = "linear_regression_model.pkl"
with open(model_filename, "wb") as pickled_model:
    pickle.dump(model, pickled_model)

with open(model_filename, "rb") as model_pkl:
    prediction_model = pickle.load(model_pkl)

new_data = pd.DataFrame(data={"income": [random.randint(1, 5), random.randint(1, 5)],
                              "cooperation_duration": [random.randint(0, 10), random.randint(0, 10)]})
print "New data set 2:"
print new_data

output = prediction_model.predict(new_data)
output_data = pd.DataFrame({"transaction": output.round()})
print "Our prediction:"
print output_data
