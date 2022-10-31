import firebase_admin as fba
from firebase_admin import credentials, storage
from firebase_admin import firestore
import datetime

import time
import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
try:
    cred = credentials.Certificate("src/firebase_tools/runebot_key.json")
except:
    cred = credentials.Certificate("../firebase_tools/runebot_key.json")
try:
    fba.initialize_app(cred, {
    'storageBucket': 'gs://dene-2ac17.appspot.com'
    })
except:
    pass
db = firestore.client()

# make a new entry with the account name and required fields

acc = 'humblejob'
db.collection(u'accounts').document(acc).create({
                                                            u'status': '',
                                                            u'last_updated': datetime.datetime.now(),
                                                            u'logged_in': False,
                                                            u'action_update_type': '',
                                                            u'action_value': '',
                                                            u'username': acc,
                                                            u'sub_action': '',
                                                            u'new_action': '',
                                                            u'last_login': datetime.datetime.now()
})