from app import app
from flask import jsonify, request, abort
from schemas import LocationSchema, EventSchema, ParticipantsSchema, TypeSchema
from models import db, Location, Event, Participant, TypeEvent, Category
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app)

admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Participant, db.session))
admin.add_view((ModelView(TypeEvent, db.session)))
admin.add_view((ModelView(Category, db.session)))


# GET /locations/ – выводит список городов или локаций
@app.route('/locations/')
def locations():
    location_schema = LocationSchema(many=True)
    locations = db.session.query(Location).all()
    serialized = location_schema.dump(locations)
    return jsonify(serialized)


# GET /events/ – выводит список ближайших событий в городе,
@app.route('/events/')
def events():
    eventtype = request.args.get('eventtype')
    location = request.args.get('location')
    event_schema = EventSchema(many=True)
    if eventtype:
        evnt = db.session.query(TypeEvent).filter(TypeEvent.code == eventtype).first_or_404()
        events = db.session.query(Event).filter(Event.types.contains(evnt)).all()
    elif location:
        loc = db.session.query(Location).filter(Location.code == location).first_or_404()
        events = db.session.query(Event).filter(Event.locations.contains(loc)).all()
    elif request.args:
        return abort(404)
    else:
        events = db.session.query(Event).all()
    serialized = event_schema.dump(events)
    return jsonify(serialized)


# POST /enrollments/ – принимает заявку на участие в событии
@app.route('/enrollments/', methods=['POST'])
@jwt_required
def enrollments_add():
    user = db.session.query(Participant).get(get_jwt_identity())
    json_data = request.get_json()
    event = db.session.query(Event).get_or_404(json_data['id'])
    if user in event.participants:
        return jsonify({"error": "You already registered"}), 400
    if event.seats > len(event.participants):
        event.participants.append(user)
        try:
            db.session.commit()
        except:
            return abort(404)
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Not enough seats"}), 400

# GET /enrollments/<enrollment_ID> - выводит список зарегистрированных пользователей на эвент
@app.route('/enrollments/<int:id>/')
def enrollments_show(id):
    event = db.session.query(Event).get(id)
    users = ParticipantsSchema(many=True)
    serialized = users.dump(event.participants)
    return jsonify(serialized)


# GET /enrollments/ - выводит список эвентов у зарегистрированного пользователя
@app.route('/enrollments/')
@jwt_required
def enrollments_participants():
    user = db.session.query(Participant).get(get_jwt_identity())
    events = EventSchema(many=True)
    serialized = events.dump(user.events)
    return jsonify(serialized)


# DELETE /enrollments/ id=<eventid> – отзывает заявку на участие в событии
@app.route('/enrollments/', methods=['DELETE'])
@jwt_required
def enrollments_del():
    if not request.is_json:
        return abort(404)
    user = db.session.query(Participant).get(get_jwt_identity())
    json_data = request.get_json()
    event = db.session.query(Event).get_or_404(json_data['id'])
    if user in event.participants:
        event.participants.remove(user)
        try:
            db.session.commit()
        except:
            return abort(404)
    else:
        return abort(404)
    return jsonify({"status": "success"})


# POST /register/ – регистрирует пользователя
@app.route('/register/', methods=['POST'])
def register():
    json_data = request.get_json()
    if json_data:
        if db.session.query(Participant).filter(Participant.email == json_data.get('email')).first():
            return jsonify({"status": "Already exists"})
        user = Participant(**json_data)
        try:
            db.session.add(user)
            try:
                db.session.commit()
            except:
                return abort(404)
        except:
            return jsonify({"status": "error"})
        usershema = ParticipantsSchema()
        serialized = usershema.dump(user)
        serialized.update(dict(password=json_data.get('password')))
        return jsonify(serialized), 201
    return jsonify({"status": "error"}), 500


# POST /auth/ – проводит аутентификацию пользователя
@app.route('/auth/', methods=['POST'])
def auth():
    if not request.is_json:
        return abort(404)
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')
    user = db.session.query(Participant).filter(Participant.email == email).first_or_404()
    if user and user.password_valid(password):
        user_schema = ParticipantsSchema(exclude=['password'])
        serialized = user_schema.dump(user)
        access_token = create_access_token(identity=user.id)
        serialized.update(dict(access_token=access_token))
        return jsonify(serialized)
    else:
        return jsonify({"error": "Wrong password"}), 400


# GET /profile/  – возвращает информацию о профиле пользователя
@app.route('/profile/<int:uid>/')
def profile(uid):
    user = db.session.query(Participant).get(uid)
    if not user:
        return jsonify({"status": "error"})
    user_schema = ParticipantsSchema(exclude=['password'])
    serialized = user_schema.dump(user)
    return jsonify(serialized)


@app.errorhandler(404)
def error(e):
    return jsonify({"status": "error"}), 500
