"""
Training linear regression
"""
import pandas as pd
import pickle
from neo4j.v1 import GraphDatabase, basic_auth
from sklearn.linear_model import LinearRegression

# Connect to database
db_location = "bolt://0.0.0.0:7687"
username = "neo4j"
password = "12345qwert"
driver = GraphDatabase.driver(db_location, auth=basic_auth(username, password))

# Work with database
with driver.session() as session:
    # erase database
    with session.begin_transaction() as clear_db:
        clear_db.run("MATCH (n) DETACH DELETE n")

    # create year
    with session.begin_transaction() as create_year:
        create_year.run("CREATE (year :Year) set year.year=2018")

        # create months
    with session.begin_transaction() as create_months:
        create_months.run(
            """MATCH (year :Year)
            WHERE year.year = 2018
            FOREACH (month IN range (4,12) | MERGE (:Month {month: month, year: 2018})-[:BELONGS_TO]->(year))""")

    # create days in April
    with session.begin_transaction() as create_days:
        create_days.run(
            """MATCH (month :Month)
            WHERE month.month = 4 AND month.year = 2018
            FOREACH(day IN range (1,30) | MERGE (:Day {day: day, month: 4, year: 2018})-[:BELONGS_TO]->(month))""")

    # create sportsmans
    with session.begin_transaction() as create_sportsmans:
        create_sportsmans.run(
            """WITH ['Anna', 'Tom', 'Nick', 'Kateryna', 'Maryna', 'Jay'] AS name
            FOREACH (i IN range(1,24) |
            CREATE (s :Sportsman {sportsmen_id: i, FullName: name[i % size(name)], age: round(rand()*34)+14, duration_training: round(rand()*8)+1}))""")

    for i in range(1, 84):
        # create training
        with session.begin_transaction() as create_training:
            create_training.run(
                """WITH round(rand()*23+1) as sportsmen_id, round(rand()*29+1) as Day, 4 as Month, 2018 as Year
                MATCH (sportsman :Sportsman), (year :Year), (month :Month), (day :Day)
                WHERE sportsman.sportsmen_id = sportsmen_id
                AND year.year=Year AND month.month=Month AND month.year=Year
                AND day.day=Day AND day.month=Month AND day.year=Year
                MERGE(sportsman)-[:HAS_TRAINING]->(day)"""
                )

    # get data from database
    with session.begin_transaction() as get_data:
        result = get_data.run(
            """MATCH(sportsman :Sportsman)-[ht :HAS_TRAINING]-(day :Day)-[:BELONGS_TO]->(:Month)-[:BELONGS_TO]->(:Year)
            WITH sportsman.sportsman_id as sportsman_id,
            sportsman.FullName as name,
            sportsman.age as age,
            sportsman.duration_training as duration_training,
            COUNT(ht) as training
            RETURN sportsman_id, name, age, duration_training, training""")
        training_data = pd.DataFrame([{k: v for k, v in r.items()} for r in result])

print "Test data set information"
print training_data
print training_data.info()

# create 2 variables called X_data and Y_data:
# X_data shall be a matrix with features columns
# and Y_data shall be a matrix with responses columns

features_columns = [x for x in training_data.columns if x not in ['sportsman_id', 'name', 'training']]
responses_columns = ['training']
X_data = training_data[features_columns]
Y_data = training_data[responses_columns]

print X_data.head()
print Y_data

y = Y_data["training"].values

print y


# give a name to Linear regression model
model_2 = LinearRegression()

# put our data to train model
model_2.fit(X_data, y)

# create new data

new_data = pd.DataFrame(data={'age': [23, 31, 17], 'duration_training': [3, 1, 2]})

print "New data set:"
print new_data

# predict a value of getting values 0 or 1
model_2.predict(new_data)
output = model_2.predict(new_data)
output_data = pd.DataFrame({'training': output})

print "Our prediction:"
print output_data

output_data['round_training'] = output_data['training'].round()
print output_data

# ------ model name -------
model_pkl_filename = 'prediction_model.pkl'
with open(model_pkl_filename, 'wb') as pickled_model:
    pickle.dump(model_2, pickled_model)

# ----- load prediction model -------
with open(model_pkl_filename, 'rb') as model_pkl:
    prediction_model = pickle.load(model_pkl)
print prediction_model

# create new data

new_data = pd.DataFrame(data = {'age': [29], 'duration_training': [1]})
print "New data set:"
print new_data

print prediction_model.predict(new_data)

