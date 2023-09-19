from marshmallow import Schema, fields


class LocationSchema(Schema):
    id = fields.Integer(dump_only=True)
    code = fields.String(required=True)
    title = fields.String(required=True)


class TypeSchema(Schema):
    id = fields.Integer(dump_only=True)
    code = fields.String(required=True)
    title = fields.String(required=True)


class EventSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(required=True)
    date = fields.DateTime(required=True)
    time = fields.DateTime(required=True)
    types = fields.Nested("TypeSchema", many=True)
    # categories =
    locations = fields.Nested("LocationSchema", many=True)
    address = fields.String(required=True)
    seats = fields.Integer(required=True)
    # participants =


class ParticipantsSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    picture = fields.String(required=True)
    location = fields.String(required=True)
    about = fields.String(required=True)
