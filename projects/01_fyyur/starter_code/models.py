from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#associative Object (different than associative table),
#connects the venue and artist models
# to form a many to many relation.
class Show(db.Model):
    #always use all lowercase for tablename.
    #if you use an uppercase name, you must use double quotes
    # when running a sql command to access table.
    #I.e select * from "Shows"
    __tablename__ = 'show'
    #ForeignKeys are always found in a child table
    #in a many to many, the associative table is always the child
    # table and in this case, Venue and Artist are the parent
    # tables
    artist_id = db.Column(db.Integer,
    db.ForeignKey('artist.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer,
    db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=True)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String((120)))
    website_link = db.Column(db.String(500))
    #the shows property is set as a relationship to the
    #association table (Show) Be sure to pass db.relationship
    # the model and not the name of the table. Notice 'Show' vs 'shows'.
    #backref creates a prop called 'venue' and adds that prop
    #to the Show model. So if you call Show.venue, it will return
    # the venue data associated with that particular show.
    #the lazy prop defines when SQLAlchemy will load data from the db.
    shows = db.relationship('Show',
    backref=db.backref('venue'),lazy='joined')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String(500))
    shows = db.relationship('Show',
    backref=db.backref('artist'),lazy='joined')
