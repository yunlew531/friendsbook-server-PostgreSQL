import os

# firebase
from firebase import Firebase
config = {
  'apiKey': os.getenv('apiKey'),
  'authDomain': os.getenv('authDomain'),
  'databaseURL': os.getenv('databaseURL'),
  'storageBucket': os.getenv('storageBucket'), 
  'serviceAccount': 'serviceAccountKey.json',
}

firebase = Firebase(config)
storage = firebase.storage()