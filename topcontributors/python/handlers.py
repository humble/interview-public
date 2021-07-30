# This file implements the backend of the application. At the bottom of the
# file is a list of routes, which map URLs to handler classes.

# Built-in Python and AppEngine imports
from datetime import datetime
from decimal import Decimal, InvalidOperation
import json
from webapp2 import RequestHandler, WSGIApplication

# Local imports (from our codebase)
from models import Order
from utils import render_jinja_template, make_random_string


class BundleHandler(RequestHandler):
  '''
  This handler represents the homepage, which implements a very simple order
  form.
  '''
  def get(self):
    template_parameters = {
      'is_employee': True,  # In a more sophisticated codebase, this would be determined by a user's account permissions
    }
    rendered_html = render_jinja_template('bundle.html', template_parameters)
    self.response.write(rendered_html)


class PlaceOrderHandler(RequestHandler):
  '''
  This handler implements an endpoint that creates a customer's order. It is
  intended to be called via AJAX and returns JSON to the browser.
  '''
  def post(self):
    # Retrieve the form data submitted by the browser
    name = self.request.get('name')
    email = self.request.get('email')
    amount_string = self.request.get('amount')

    amount_in_pennies = self.convert_amount_string_to_pennies(amount_string)
    if email and amount_in_pennies:
      # Create the new order and write it to the database
      transaction_id = self.create_new_order(name, email, amount_in_pennies)

      # Return JSON to the browser indicating a successful purchase
      self.response.write(json.dumps({
        'success': True,
        'message': 'Successfully created order. Your transaction ID is ' + transaction_id,
      }))

    else:
      # Return JSON to the browser indicating an error
      self.response.write(json.dumps({
        'success': False,
        'message': 'Please enter an email address and an amount to pay.',
      }))

  def create_new_order(self, name, email, amount_in_pennies):
    '''
    Writes a new order to the database with the given parameters. Returns the
    transaction ID of the new order.
    '''
    new_order = Order()
    new_order.created = datetime.utcnow()
    new_order.name = name
    new_order.email = email
    new_order.transaction_id = make_random_string(12)
    new_order.pennies_paid = amount_in_pennies
    new_order.put()
    return new_order.transaction_id

  def convert_amount_string_to_pennies(self, amount_string):
    '''
    Converts a string containing an amount to pay, in US dollars, to an
    integer representing the number of pennies. If the amount cannot be
    converted, this function returns None.
    '''
    amount_string = amount_string.strip()

    # Strip out a leading dollar sign, if present
    if amount_string.startswith('$'):
      amount_string = amount_string[1:]

    # Convert the string to a number of pennies
    try:
      return int(Decimal(amount_string) * 100)
    except InvalidOperation:
      # This means amount_string is in an invalid format
      return None


class OrderLookupHandler(RequestHandler):
  '''
  This handler implements a simple tool to look up and display details
  about a customer's order. It might be used by a Customer Support team.
  '''

  def render_page(self, orders=[], error_text=None):
    template_parameters = {
      'orders': orders,
      'error_text': error_text,
    }
    rendered_html = render_jinja_template('order_lookup.html', template_parameters)
    self.response.write(rendered_html)

  def get(self):
    self.render_page()

  def post(self):
    # Retrieve the transaction ID submitted by the browser
    transaction_id = self.request.get('transaction_id')

    if transaction_id:
      # Find any orders in the database with this transaction ID
      MAX_ORDERS_TO_FETCH = 5
      orders = Order.query().filter(Order.transaction_id == transaction_id).fetch(MAX_ORDERS_TO_FETCH)
      if orders:
        self.render_page(orders=orders)
      else:
        self.render_page(error_text='No orders found with that Transaction ID.')

    else:
      self.render_page(error_text='You must enter a Transaction ID.')


# This is a list of "routes". This maps URLs from the browser to the handler
# classes defined above.
#
# Each route is a tuple with two values: a regular expression and a class.
# For each request from the browser, AppEngine will find the first regular
# expression in this list that matches the URL. It will then call either the
# get() or post() function on the class, depending on whether this is a GET or
# POST request.
#
# For more information, see: http://webapp2.readthedocs.io/en/latest/guide/routing.html
app = WSGIApplication(
  routes=[
    (r'/place-order', PlaceOrderHandler),
    (r'/order-lookup', OrderLookupHandler),
    (r'/', BundleHandler),
  ],
)
