'''Server web framework.'''

from __future__ import print_function

import time
import logging
import google.cloud.logging
from database import Database
from flask_cors import CORS
from flask_compress import Compress
from firebase_admin import firestore
from flask import Flask, request, jsonify

import primes
import load_firebase
from helpers import is_str, InvalidRequest

MAX_SOURCE_NUMBER_DIGITS_COUNT = 4000

# Connect to the local database.
database = Database()

# Initialize the Flask app.
app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Add support for cross-origin requests.
CORS(app)

# Add gzip compression.
Compress(app)

# Create a Firestore client
firestore_client = firestore.client()


def load_app(environment='development'):
  '''Gunicorn entry point.'''
  if environment == 'staging' or environment == 'production':
    # Initialize GCP logging (non-development only).
    logging.info('Starting app in %s mode with remote logging enabled...', environment)
    logging_client = google.cloud.logging.Client()
    logging_client.setup_logging()

  return app


@app.errorhandler(500)
@app.errorhandler(Exception)
def unhandled_exception_handler(error):
  '''Unhandled exception handler.'''
  logging.exception('Internal server error: %s', {
      'error': error,
      'data': request.data
  })

  return jsonify({
      'error': {
          'code': 'INTERNAL_SERVER_ERROR',
          'message': 'An unexpected internal server error occurred. Please try again.'
      }
  }), 500


@app.errorhandler(404)
@app.errorhandler(405)
def route_not_found_handler(error):
  '''Route not found handler.'''
  logging.warning('Route not found: %s %s', request.method, request.path)
  return jsonify({
      'error': {
          'code': 'ROUTE_NOT_FOUND',
          'message': 'Route not found: {0} {1}'.format(request.method, request.path)
      }
  }), 404


@app.errorhandler(InvalidRequest)
def invalid_request_handler(error):
  '''Invalid request handler.'''
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


@app.route('/ok', methods=['GET'])
def ok_endpoint():
  '''Health check endpoint.'''
  return jsonify({
      'timestamp': int(round(time.time() * 1000))
  })


@app.route('/primes', methods=['POST'])
def primes_endpoint():
  '''Generates a prime number which is close to the provided number.

    Args:
      None

    Returns:
      dict: An empty dict.

    Raises:
      InvalidRequest: If the required number is missing or invalid.
  '''
  start_time = time.perf_counter()

  if (request.json is None or 'number' not in request.json):
    raise InvalidRequest({
        'code': 'INVALID_ARGUMENT',
        'message': 'The "number" body argument must be provided.'
    })
  elif ('postId' not in request.json):
    raise InvalidRequest({
        'code': 'INVALID_ARGUMENT',
        'message': 'The "postId" body argument must be provided.'
    })

  number_str = request.json['number']
  post_id = request.json['postId']

  if (len(number_str) > MAX_SOURCE_NUMBER_DIGITS_COUNT):
    raise InvalidRequest({
        'code': 'INVALID_ARGUMENT',
        'message': 'The "number" body argument must have at most {0} digits.'.format(MAX_SOURCE_NUMBER_DIGITS_COUNT)
    })

  try:
    number_long = long(number_str)
  except:
    raise InvalidRequest({
        'code': 'INVALID_ARGUMENT',
        'message': '"number" body argument must be a string representation of a number.'
    })

  if (not is_str(post_id) or post_id == ''):
    raise InvalidRequest({
        'code': 'INVALID_ARGUMENT',
        'message': 'The "postId" body argument must be a non-empty string.'
    })

  is_cached_result = True
  candidate_prime = database.lookup_source_number(number_str)
  if candidate_prime is None:
    is_cached_result = False
    candidate_prime = primes.find_nearby_candidate_prime(number_long, len(number_str))

  # Log an warning and return an error response if no candidate prime was found.
  if candidate_prime is None:
    message = 'No candidate prime number found near {0}.'.format(number_str)

    logging.warning(message)

    raise InvalidRequest({
        'code': 'CANDIDATE_PRIME_NOT_FOUND',
        'message': message
    })

  candidate_prime_str = str(candidate_prime)

  # Add the connection to Firestore.
  try:
    firestore_client.collection(u'posts').document(post_id).update({
        u"primeImage": {
            u"primeNumberString": unicode(candidate_prime_str, "utf-8")
        }
    })
  except Exception as error:
    logging.error('Failed to add candidate prime to Firestore: %s', {
        'error': error,
        'post_id': post_id,
        'candidate_prime': candidate_prime
    })

  if not is_cached_result:
    try:
      database.insert_result({
          'source_number': number_str,
          'result': candidate_prime_str,
          'duration': time.perf_counter() - start_time,
      })
    except Exception as error:
      logging.error('Failed to save result to SQLite file: %s', {
          'error': error,
          'source_number': number_str,
          'result': candidate_prime_str,
          'duration': time.perf_counter() - start_time,
      })

  return jsonify(candidate_prime_str)
