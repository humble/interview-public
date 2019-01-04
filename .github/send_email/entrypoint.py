#!/usr/bin/env python

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import formataddr
import json
import os
import smtplib


EMAIL_ADDRESS_FOR_MASTER_COMMITS = 'realeng@humblebundle.com'

SENDGRID_SMTP_USERNAME = 'apikey'  # This is always the username for Sendgrid API keys


def parse_input():
  """Returns a data structure containing all input provided by GitHub.
  """
  event_path = os.getenv('GITHUB_EVENT_PATH')
  with open(event_path, 'r') as file_handle:
    return json.load(file_handle)


def does_payload_contain_commits(event_payload):
  """Returns True if event_payload contains at least one pushed commit; False
  otherwise. This allows you to ignore things like pushed tags, which do not
  contain commits.
  """

  # A pushed commit is to refs/heads/BRANCHNAME
  # A pushed tag is to refs/tags/TAGNAME
  if not event_payload['ref'].startswith('refs/heads/'):
    return False

  # Some branch-related pushes don't have any commits. For example, deleting a
  # branch, or pushing a branch without any changes.
  commits = event_payload.get('commits', [])
  return len(commits) > 0


def get_formatted_author_email_address(event_payload):
  """Returns the fully-formatted email address of the user who caused this event.
  """

  pusher_email = event_payload['pusher']['email']
  pusher_github_username = event_payload['pusher']['name']

  # Unfortunately, the 'pusher' key does not contain the real name, so check
  # the pushed commits to try to find it. There are situatons where none of
  # the commits will be from the pusher; when that happens, we use the github
  # username as a fallback.
  name_to_use = pusher_github_username
  for commit_payload in event_payload['commits']:
    if commit_payload['author']['username'] == pusher_github_username:
      name_to_use = commit_payload['author']['name']
      break

  return formataddr((name_to_use, pusher_email))


def format_subject_line(event_payload):
  """Returns a string containing the intended subject line for the email.
  """
  full_repo_name = event_payload['repository']['full_name']
  head_commit = event_payload['head_commit']

  MAX_COMMIT_HASH_LENGTH = 6  # This might be too short to be unique in some circumstances; but conforms to what GitHub's emails used to do
  commit_hash = head_commit['id'][:MAX_COMMIT_HASH_LENGTH]

  MAX_COMMIT_MESSAGE_LENGTH = 50
  commit_message_first_line = head_commit['message'].split('\n')[0]
  if len(commit_message_first_line) > MAX_COMMIT_MESSAGE_LENGTH:
    commit_message_first_line = commit_message_first_line[:MAX_COMMIT_MESSAGE_LENGTH] + '...'

  return '[%s] %s: %s' % (full_repo_name, commit_hash, commit_message_first_line)


def format_body(event_payload):
  """Returns a string containing the intended body for the email.
  """
  lines = []
  lines.append('Branch: %s' % event_payload['ref'])
  lines.append('Home:   %s' % event_payload['repository']['html_url'])

  for commit_payload in event_payload['commits']:
    lines += get_body_lines_for_single_commit(commit_payload)

  if len(event_payload['commits']) > 1:
    lines.append('Compare: %s' % event_payload['compare'])

  return '\n'.join(lines)


def get_body_lines_for_single_commit(commit_payload):
  """Returns a list of strings representing lines to add to the email body
  representing the given commit.
  """

  commit_date = iso_timestamp_to_pacific_date(commit_payload['timestamp'])

  added_files = commit_payload.get('added', [])
  removed_files = commit_payload.get('removed', [])
  modified_files = commit_payload.get('modified', [])

  lines = []
  lines.append('Commit: %s' % commit_payload['id'])
  lines.append('    %s' % commit_payload['url'])
  lines.append('Author: %s <%s>' % (commit_payload['author']['name'], commit_payload['author']['email']))
  lines.append('Date:   %s (%s)' % (commit_date.strftime('%Y-%m-%d'), commit_date.strftime('%a, %d %b %Y')))

  if added_files or removed_files or modified_files:
    all_files_with_type = []
    all_files_with_type += [(filename, 'A') for filename in added_files]
    all_files_with_type += [(filename, 'R') for filename in removed_files]
    all_files_with_type += [(filename, 'M') for filename in modified_files]
    all_files_with_type.sort(key=lambda file_tuple: file_tuple[0])

    lines.append('')
    lines.append('Changed paths:')
    for filename, change_type in all_files_with_type:
      lines.append('  %s %s' % (change_type, filename))

  lines.append('')
  lines.append('Log Message:')
  lines.append('-----------')
  lines.append(commit_payload['message'])
  lines.append('')
  lines.append('')

  return lines


def iso_timestamp_to_pacific_date(timestamp_string):
  """This implements a simple timestamp parser and returns it as a date object
  relative to the Pacific timezone. This is intended to avoid the need for the
  overhead of a full-scale date parsing library like dateutil.

  WARNING: Currently, this function always assumes PST (UTC-8). The 1-hour
  difference between PST and PDT is not worth the bother of handling for how
  this function is currently being used.
  """

  PACIFIC_TIME_OFFSET_IN_HOURS = -8

  # Start with the standard portion of all ISO datetime formats
  format_string = '%Y-%m-%dT%H:%M:%S'

  # Figure out if we have a millisecond section; if so, add to format_string
  if '.' in timestamp_string:
    format_string += '.%f'

  # Parse and remove the timezone section, if present
  timestamp_string_after_date_portion = timestamp_string.split('T', 1)[1]
  if timestamp_string_after_date_portion.endswith('Z'):
    timestamp_string = timestamp_string[:-1]
    timezone_offset_minutes = 0
  elif '+' in timestamp_string_after_date_portion:
    timestamp_string, timezone_info = timestamp_string.rsplit('+', 1)
    timezone_info = timezone_info.replace(':', '')
    timezone_offset_minutes = int(timezone_info[:2]) * 60 + int(timezone_info[2:])
  elif '-' in timestamp_string_after_date_portion:
    timestamp_string, timezone_info = timestamp_string.rsplit('-', 1)
    timezone_info = timezone_info.replace(':', '')
    timezone_offset_minutes = -(int(timezone_info[:2]) * 60 + int(timezone_info[2:]))
  else:
    # No timezone information -- assume UTC
    timezone_offset_minutes = 0

  # Parse string
  dt = datetime.strptime(timestamp_string.strip(), format_string)

  # Convert to UTC
  dt -= timedelta(minutes=timezone_offset_minutes)

  # Convert to Pacific Time
  dt += timedelta(hours=PACIFIC_TIME_OFFSET_IN_HOURS)

  # Return as date
  return dt.date()


def send_email_about_commits(event_payload):
  """Formats and sends an email about the commits in the given payload.
  """
  is_master = event_payload['ref'] == 'refs/heads/master'
  from_address = get_formatted_author_email_address(event_payload)
  recipient_address = EMAIL_ADDRESS_FOR_MASTER_COMMITS if is_master else from_address

  msg = MIMEText(format_body(event_payload))
  msg['Subject'] = format_subject_line(event_payload)
  msg['From'] = from_address
  msg['To'] = recipient_address

  s = smtplib.SMTP('smtp.sendgrid.net', 587)
  s.login(SENDGRID_SMTP_USERNAME, os.getenv('SENDGRID_PASSWORD'))
  s.sendmail(from_address, [recipient_address], msg.as_string())
  s.quit()


def main():
  event_payload = parse_input()
  if does_payload_contain_commits(event_payload):
    send_email_about_commits(event_payload)


if __name__ == '__main__':
  main()
