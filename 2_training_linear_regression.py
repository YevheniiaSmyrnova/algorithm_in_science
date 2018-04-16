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

    # # create year
    # with session.begin_transaction() as create_year:
    #     create_year.run("CREATE (year :Year) set year.year=2018")
    #
    #     # create months
    # with session.begin_transaction() as create_months:
    #     create_months.run(
    #         """MATCH (year :Year)
    #         WHERE year.year = 2018
    #         FOREACH (month IN range (4,12) | MERGE (:Month {month: month, year: 2018})-[:BELONGS_TO]->(year))""")
    #
    # # create days in April
    # with session.begin_transaction() as create_days:
    #     create_days.run(
    #         """MATCH (month :Month)
    #         WHERE month.month = 4 AND month.year = 2018
    #         FOREACH(day IN range (1,30) | MERGE (:Day {day: day, month: 4, year: 2018})-[:BELONGS_TO]->(month))""")
    #
    # # create sportsmans
    # with session.begin_transaction() as create_sportsmans:
    #     create_sportsmans.run(
    #         """WITH ["Anna", "Tom", "Nick", "Kateryna", "Maryna", "Jay"] AS name
    #         FOREACH (i IN range(1,24) |
    #         CREATE (s :Sportsman {sportsmen_id: i, FullName: name[i % size(name)], age: round(rand()*34)+14, duration_training: round(rand()*8)+1}))""")
    #
    # for i in range(1, 84):
    #     # create training
    #     with session.begin_transaction() as create_training:
    #         create_training.run(
    #             """WITH round(rand()*23+1) as sportsmen_id, round(rand()*29+1) as Day, 4 as Month, 2018 as Year
    #             MATCH (sportsman :Sportsman), (year :Year), (month :Month), (day :Day)
    #             WHERE sportsman.sportsmen_id = sportsmen_id
    #             AND year.year=Year AND month.month=Month AND month.year=Year
    #             AND day.day=Day AND day.month=Month AND day.year=Year
    #             MERGE(sportsman)-[:HAS_TRAINING]->(day)"""
    #             )
    #
    # # get data from database
    # with session.begin_transaction() as get_data:
    #     result = get_data.run(
    #         """MATCH(sportsman :Sportsman)-[ht :HAS_TRAINING]-(day :Day)-[:BELONGS_TO]->(:Month)-[:BELONGS_TO]->(:Year)
    #         WITH sportsman.sportsman_id as sportsman_id,
    #         sportsman.FullName as name,
    #         sportsman.age as age,
    #         sportsman.duration_training as duration_training,
    #         COUNT(ht) as training
    #         RETURN sportsman_id, name, age, duration_training, training""")
    #     training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

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
