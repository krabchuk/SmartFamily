import os

# Set your api tokens and proxy through environmental variables
# (add lines to your .bashrc and restart terminal):
# export BOT_TOKEN='XXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

token = os.getenv('SMART_FAMILY_BOT_TOKEN')
assert token is not None, 'Problem in reading SMART_FAMILY_BOT_TOKEN variable. Read tokens.py for information'
