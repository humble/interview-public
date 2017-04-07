# This file contains useful utility functions that can be used from your
# handlers. You do not need to modify this file, although you are welcome to
# add new functions here if you want.

# Built-in Python imports
import jinja2
import os
import random
import string


TEMPLATES_DIRECTORY = 'templates'


def render_jinja_template(filename, template_parameters=None):
  '''
  This function renders a Jinja template and returns a string containing the
  output. Optionally, you can pass parameters to the template.

  For more information on Jinja, see: http://jinja.pocoo.org/docs/2.9/
  '''
  jinja_loader = jinja2.FileSystemLoader([TEMPLATES_DIRECTORY])
  jinja_environment = jinja2.Environment(
    loader=jinja_loader,
    auto_reload=True,
  )
  jinja_template = jinja_environment.get_template(filename)
  return jinja_template.render(template_parameters or {})


def make_random_string(string_length):
  '''
  This function returns a random string of the requested length, containing
  uppercase letters and numbers.
  '''
  # From http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(string_length))
