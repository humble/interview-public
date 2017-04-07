# This file implements database models used by the application. A model is
# similar to an SQL table. A model contains one or more properties, which
# are similar to columns in an SQL table.

# Built-in Python and AppEngine imports
from google.appengine.ext import db


class Order(db.Model):
  '''
  This class represents a single customer's purchase of a bundle.
  '''

  # The datetime at which the customer placed the order
  created = db.DateTimeProperty()

  # The customer's name
  name = db.StringProperty()

  # The customer's email address
  email = db.StringProperty()

  # A unique ID for this transaction
  transaction_id = db.StringProperty()

  # How much money the customer paid, in pennies
  pennies_paid = db.IntegerProperty()
