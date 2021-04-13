#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_sqlalchemy import SQLAlchemy
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
    )
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Show, Venue, Artist

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db.init_app(app)
app.config.from_object('config')
moment = Moment(app)
migrate = Migrate(app, db, compare_type=True)
csrf = CSRFProtect(app)

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
  #TODO: Create an empty array
  locals=[]
  # TODO: store venue data in a variable
  venues=Venue.query.all()
  # TODO: Next we need to collect all combinations
  # of city and state from the db. ALso we need to
  # limit our results to a max of one city and state
  # combination. Store results in another variable.
  places= Venue.query.distinct(Venue.city, Venue.state).all()
  # TODO: The query returns a list, therefor
  # we can iterate over the list to efficiently
  # build our objects that we will add to the locals list
  for place in places:
      #build and append each place obj
      locals.append({
        'city': place.city,
        'state': place.state,
        #we have access to venues because of the trailing
        #for venue in venues
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            #by utilizing the shows relationship on the venues
            # table, we can retrieve all of the shows associated
            # with a specific venue. Then we loop over each show
            # and only return shows who's start time is greater
            # then the current date and time
            'num_upcoming_shows': len([
            show for show in venue.shows
            if show.start_time > datetime.now()])
        } for venue in venues
        if venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals);
@csrf.exempt
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
  # TODO: Get venue data from db based on id
  # We need to take the existing venue data and
  # add two properties. Upcoming and past shows
  # each should have a list of shows in which the
  # start_time has already past or is upcoming
  venue = Venue.query.get(venue_id)
  #declare and set to empty list
  past_shows=[]
  upcoming_shows=[]
  # venue.shows is not a column but it is a relationship.
  # Becuase we set lazy='joined' on our relationship key in
  # our venue model, when we query our venue, we also recieve
  # all relational data for that venue and the corresponding Shows.
  # loop over each show returned to us.
  for show in venue.shows:
      #build temp_show object with keys accesible by the
      # template we are sending our data to.
      #again, we have access to artist keys because
      #our query returned all shows related to our venue
      # and every show has a relationship to an artist.
      # This is how we are able to access artist.name
      temp_show= {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%m/%d/%Y, %H:%M')
      }
      #compare start_time to current date and time,
      #if it is less than or equal to, then the show
      # has passed. Else the show has not started yet
      if show.start_time <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)
#vars is needed to assign the value of data to the
#venue dictionary. This is how data gets all the venue
# keys and values, much more effecient than how i did it
# before
  data=vars(venue)
#now that data has the venue data, we need to add
#our past and upcoming shows list of objects as well
# a past shows count and upcoming shows count.
  data['past_shows']=past_shows
  data['upcoming_shows']=upcoming_shows
  data['past_shows_count']=len(past_shows)
  data['upcoming_shows_count']=len(upcoming_shows)

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
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
          venue = Venue()
          form.populate_obj(venue)
          db.session.add(venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')

      except ValueError:
          db.session.rollback()
          print(e)

      finally:
          db.session.close()
  else:
      message=[]
      for field, err in form.errors.items():
          message.append(field + ' '+ '|'.join(err))
          flash('Errors' + str(message))

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
@csrf.exempt
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
  # TODO: retrieve artist dictionary based on provided id.
  # build data obj with artist dictionary and build past and
  # upcoming shows list.
  artist = Artist.query.get(artist_id)
  upcoming_shows=[]
  past_shows=[]
  #loop over each show related to artist
  for show in artist.shows:
  # build temp_show
      temp_show={
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime('%m/%d/%Y, %H:%M')
      }
      if show.start_time <= datetime.now():
          past_shows.append(temp_show)
      else:
          upcoming_shows.append(temp_show)

  data=vars(artist)
  data['upcoming_shows']=upcoming_shows
  data['upcoming_shows_count']=len(upcoming_shows)
  data['past_shows']=past_shows
  data['past_shows_count']=len(past_shows)

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
  form=ArtistForm(request.form,meta={'csrf': False})
  if form.validate():
      try:
          artist = Artist.query.get(artist_id)
          artist.name=form.name.data
          artist.city=form.city.data
          artist.state=form.state.data
          artist.genres=form.genres.data
          artist.phone=form.phone.data
          artist.image_link=form.image_link.data
          artist.facebook_link=form.facebook_link.data
          artist.website_link=form.website_link.data
          artist.seeking_venue=form.seeking_venue.data
          artist.seeking_description=form.seeking_description.data
          db.session.commit()
      except Exception as e:
          print(e)
          db.session.rollback()
      finally:
          db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
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
  venue=Venue.query.get(venue_id)
  form = VenueForm(request.form,meta={'csrf': False})
  if form.validate():
    try:
      venue.name = form.name.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.genres= form.genres.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      db.session.commit()
    except ValueError as e:
      db.session.rollback()
      print(e)
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
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
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
          artist=Artist()
          form.populate_obj(artist)
          db.session.add(artist)
          db.session.commit()
          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
          # TODO: on unsuccessful db insert, flash an error instead.
      except ValueError as e:
          db.session.rollback()
          print(e)
          flash('An error occurred. Artist ' + data.name
          + ' could not be listed.')
      finally:
          db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
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
  form=ShowForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
          show=Show()
          form.populate_obj(show)
          db.session.add(show)
          db.session.commit()
          # on successful db insert, flash success
          flash('Show was successfully listed!')

      except Exception as e:
          print(e)
          db.session.rollback()

      finally:
          db.session.close()
  else:
      message = []
      for field, err in form.errors.items():
          message.append(field + ' ' + '|'.join(err))
          flash('Errors ' + str(message))
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
