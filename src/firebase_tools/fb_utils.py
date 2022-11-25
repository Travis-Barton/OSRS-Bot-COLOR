import firebase_admin as fba
from firebase_admin import credentials, storage
from firebase_admin import firestore
import datetime
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path + "\\runebot_key.json")
try:
    cred = credentials.Certificate(dir_path + "\\runebot_key.json")
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

acc = 'math4you'
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