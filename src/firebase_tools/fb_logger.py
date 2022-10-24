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


def update_status(acc, status, action_update_type, action_value, last_login=None,
                  logged_in=True):
    try:
        if last_login is not None:
            last_login = datetime.datetime.now()
            db.collection(u'accounts').document(acc).update({
                u'last_login': last_login,
            })
        db.collection(u'accounts').document(acc).update({
                                                            u'status': status,
                                                            u'last_updated': datetime.datetime.now(),
                                                            u'logged_in': logged_in,
                                                            u'action_update_type': action_update_type,
                                                            u'action_value': action_value
        })
        return True
    except Exception as e:
        print(e)
        return False


def new_action_available(acc) -> bool:
    val = db.collection(u'accounts').document(acc).get().to_dict()['new_action']
    if val != '':
        return True
    else:
        return False


def get_action(acc) -> str:
    val = db.collection(u'accounts').document(acc).get().to_dict()['new_action']
    if val != '':
        return val
    else:
        return ''


def wipe_new_action(acc):
    db.collection(u'accounts').document(acc).update({
        'new_action': ''})


def upload_to_firebase(filepath):
    bucket = storage.bucket('runebot-d7855.appspot.com')
    blob = bucket.blob('runepics/' + filepath)
    # with open(filepath, 'rb') as my_file:
    #     blob.upload_from_file(my_file)
    blob.upload_from_filename(filepath)


if __name__ == '__main__':
    # get main bot data
    doc = db.collection(u'accounts').document(u'travmanman').get()
    if doc.exists:
        trav = doc.to_dict()
        print(trav.keys())
        print(f'check if I\'m logged in: {trav["logged_in"]}')
        if trav["sub_action"] == '':
            print('no sub action')
        else:
            print(f'sub action: {trav["sub_action"]}')
    upload_to_firebase('README.md')
