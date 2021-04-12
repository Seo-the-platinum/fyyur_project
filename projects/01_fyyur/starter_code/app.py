#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:seoisoe5i73@localhost:5432/artist_booking_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#associative Object (different than associative table),
#connects the venue and artist models
# to form a many to many relation.
class Show(db.Model):
    #always use all lowercase for tablename.
    #if you use an uppercase name, you must use double quotes
    # when running a sql command to access table.
    #I.e select * from "Shows"
    __tablename__ = 'shows'
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
    backref=db.backref('venue'),lazy=True)
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
    backref=db.backref('artist'),lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # First we declare an empty list call areas. What we want to do
  # is collect all of the city and state combinations from our venues
  # and create a list with only one instance of each combo.
  # Our areas list should contain two objects when done.
  # areas[0] = {San Francisco, CA}, areas[1] = {New York, NY}
  areas=[]
  #places will collect the the different city and state combinations
  #from each venue. Becuase we are using query.distinct, the db
  # will only return different combos.For example, once san Francisco, CA
  # has been found, any other venue with that same city and state combo
  # will not be returned from the db.
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  #once we hace all of our different locations, we loop over them
  #to create an area object with a city and state prop. Notice that
  # the objects keys are strings and must be accessed by using
  # area['city'] and area['place']. area.city and area.state will not work
  for place in places:
      area= {
      'city': place.city,
      'state': place.state
      }
      #at the end of each loop, append the area object to the
      #area list
      areas.append(area)
  #now we need to collect the id and name from each venue and
  # add them to the area objects we just created
  venues = Venue.query.all()
  #once we have venues data, loop over the areas list
  for area in areas:
      #for each area obj, create a venues key with a value of
      # an empty list. each are obj will have a list of all Venues
      # whos city and state match its city and state values
      area['venues']= []
      for venue in venues:
          #if statement to check if the venue city and state are the same
          # as the area obj city and state. if it is, create an obj and
          # append to the venues key in area.
          if venue.city == area['city'] and venue.state == area['state']:
              v = {
                'id': venue.id,
                'name': venue.name
              }
              area['venues'].append(v)
  #pass areas data to areas prop for venues html
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  count = 0
  response = {}
  data = []

  search = request.form.get('search_term')
  filtered_venues = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
  response['count'] = len(filtered_venues)
  response['data'] = filtered_venues
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()
# what is this query trying to get? we want all the data from the show
# and artist tables. Create a new table with all artist and show data
# compare the combined table with show first and then to venue. return data
# from artist an show tables that meet the filter requirements
#
  upcoming_shows= db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
      Show.venue_id == venue_id,
      Show.artist_id == Artist.id,
      Show.start_time > datetime.now()
    ).\
    all()

  print(db.session.query(Artist, Show))
  data ={
  'id': venue.id,
  'name': venue.name,
  'address': venue.address,
  'city': venue.city,
  'state': venue.state,
  'phone': venue.phone,
  'genres': venue.genres,
  'image_link': venue.image_link,
  'facebook_link': venue.facebook_link,
  'website': venue.website_link,
  'seeking_talent': venue.seeking_talent,
  'seeking_description': venue.seeking_description,
  'upcoming_shows': [{
    'artist_id': artist.id,
    'artist_name':artist.name,
    'artist_image_link': artist.image_link,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
   } for artist, show in upcoming_shows],
  'past_shows': [{
    'artist_id': artist.id,
    'artist_name': artist.name,
    'artist_image_link': artist.image_link,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
   } for artist, show in past_shows],
  'upcoming_shows_count': len(upcoming_shows),
  'past_shows_count': len(past_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = VenueForm(request.form)
  try:
      seeking_talent = False
      seeking_description = ''
      if 'seeking_talent' in request.form:
          seeking_talent = request.form['seeking_talent'] == 'y'
      if 'seeking_description' in request.form:
          seeking_description = request.form['seeking_description']
      newVenue = Venue(
        name=request.form['name'],
        genres=request.form.getlist('genres'),
        address=request.form['address'],
        city=request.form['city'],
        state=request.form['state'],
        phone=request.form['phone'],
        website_link=request.form['website_link'],
        facebook_link=request.form['facebook_link'],
        image_link=request.form['image_link'],
        seeking_talent=seeking_talent,
        seeking_description=seeking_description,
      )
      db.session.add(newVenue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except ValueError:
      db.session.rollback()
      print(e)

  finally:
      db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      deleteVenue= Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      return render_template('pages/home.html')

  except Exception as e:
      print(e)
      db.session.rollback()

  finally:
      db.session.close()
  return redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  search = request.form.get('search_term')
  filtered_artists = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()
  response['count'] = len(filtered_artists)
  response['data'] = filtered_artists
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist= Artist.query.get(artist_id)
  upcoming_shows= db.session.query(Venue, Show).join(Show).\
  join(Artist)\
  .filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time > datetime.now()
  ).all()

  past_shows = db.session.query(Venue, Show).join(Show).\
  join(Artist)\
  .filter(
    Show.artist_id == artist_id,
    Show.venue_id == Venue.id,
    Show.start_time < datetime.now()
  ).all()
  data = {
   'id': artist.id,
   'name': artist.name,
   'city': artist.city,
   'state': artist.state,
   'phone': artist.phone,
   'genres': artist.genres,
   'image_link': artist.image_link,
   'facebook_link': artist.facebook_link,
   'website': artist.website_link,
   'seeking_venue': artist.seeking_venue,
   'seeking_description': artist.seeking_description,
   'upcoming_shows': [{
     'venue_id': venue.id,
     'venue_name':venue.name,
     'venue_image_link': venue.image_link,
     "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for venue, show in upcoming_shows],
   'past_shows': [{
     'venue_id': venue.id,
     'venue_name':venue.name,
     'venue_image_link': venue.image_link,
     "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in past_shows],
   'upcoming_shows_count': len(upcoming_shows),
   'past_shows_count': len(past_shows)
   }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form=ArtistForm(request.form)
  try:
      seeking_venue = False
      seeking_description = ''
      if request.form['seeking_venue']:
          seeking_venue = request.form['seeking_venue'] == 'y'
      if request.form['seeking_description']:
          seeking_description = request.form['seeking_description']
      artist = Artist.query.get(artist_id)
      artist.name=request.form['name']
      artist.city=request.form['city']
      artist.state=request.form['state']
      artist.genres=request.form.getlist('genres')
      artist.phone=request.form['phone']
      artist.image_link=request.form['image_link']
      artist.facebook_link=request.form['facebook_link']
      artist.website_link=request.form['website_link']
      artist.seeking_venue=seeking_venue
      artist.seeking_description=seeking_description
      db.session.commit()

  except Exception as e:
      print(e)
      db.session.rollback()

  finally:
      db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
      seeking_talent = False
      seeking_description = ''
      if request.form['seeking_talent']:
          seeking_talent = request.form['seeking_talent'] == 'y'
      if request.form['seeking_description']:
          seeking_description = request.form['seeking_description']
      venue = Venue.query.get(venue_id)
      venue.name = request.form['name']
      venue.address = request.form['address']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.genres= request.form.getlist('genres')
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
      venue.phone = request.form['phone']
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      venue.website_link = request.form['website_link']
      db.session.commit()
  except ValueError:
      db.session.rollback()
      print(e)
  finally:
      db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      seeking_venue=False
      seeking_description=''
      if request.form['seeking_venue']:
          seeking_venue = request.form['seeking_venue'] == 'y'
      if request.form['seeking_description']:
          seeking_description = request.form['seeking_description']
      newArtist = Artist(
        name=request.form['name'],
        city=request.form['city'],
        state=request.form['state'],
        image_link=request.form['image_link'],
        facebook_link=request.form['facebook_link'],
        genres=request.form.getlist('genres'),
        website_link=request.form['website_link'],
        phone=request.form['phone'],
        seeking_description=seeking_description,
        seeking_venue=seeking_venue,
      )
      db.session.add(newArtist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      # TODO: on unsuccessful db insert, flash an error instead.
  except ValueError:
      flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data= []
  for show in shows:
      venue=Venue.query.get(show.venue_id)
      artist=Artist.query.get(show.artist_id)
      data.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm(request.form)
  try:
      show=Show(
        artist_id= request.form['artist_id'],
        start_time= request.form['start_time'],
        venue_id= request.form['venue_id']
      )
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')

  except Exception as e:
      print(e)
      db.session.rollback()

  finally:
      db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
