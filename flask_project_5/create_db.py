import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from models import Event, Location, Category, TypeEvent, create_app, db
from datetime import datetime

app = create_app()
app.config.from_object('config')
app.app_context().push()

# engine = db.create_engine('sqlite:///test.db', engine_opts={})
db.create_all()

events = pd.read_csv('https://stepik.org/media/attachments/course/61900/meetup_events.csv')
events = events.dropna()
locations = pd.read_csv('https://stepik.org/media/attachments/course/61900/meetup_locations.csv')
locations = locations.dropna()
categories = pd.read_csv('https://stepik.org/media/attachments/course/61900/meetup_categories.csv')
types = pd.read_csv('https://stepik.org/media/attachments/course/61900/meetup_types.csv')

# locations.to_sql('locations', con=engine, index=False)
# categories.to_sql('categories', con=engine, index=False, if_exists='replace')
# types.to_sql('types', con=engine, index=True, index_label='id', if_exists='replace')

for row in locations.values.tolist():
    loc = Location(
        code=row[0],
        title=row[1]
    )
    db.session.add(loc)

for row in categories.values.tolist():
    cat = Category(
        code=row[0],
        title=row[1]
    )
    db.session.add(cat)

for row in types.values.tolist():
    type = TypeEvent(
        code=row[0],
        title=row[1]
    )
    db.session.add(type)

try:
    db.session.commit()
except:
    print('Error!')

for idx, row in events.iterrows():
    event = Event(
        title=row['title'],
        description=row['description'],
        date=datetime.strptime(row['date'], "%d.%m.%Y"),
        time=datetime.strptime(row['time'], "%H:%M"),
        address=row['address'],
        seats=row['seats']
    )
    for location in row['location'].split():
        loc = db.session.query(Location).filter(Location.code == location.strip(', ')).first()
        event.locations.append(loc)

    for type in row['type'].split():
        q = db.session.query(TypeEvent).filter(TypeEvent.code == type.strip(', ')).first()
        event.types.append(q)

    for cat in row['category'].split():
        q = db.session.query(Category).filter(Category.code == cat.strip(', ')).first()
        event.categories.append(q)
        db.session.add(event)
    db.session.commit()
