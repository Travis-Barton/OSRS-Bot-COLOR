import firebase_admin as fba
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import time
import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
cred = credentials.Certificate("src/firebase/runebot_key.json")
fba.initialize_app(cred)
db = firestore.client()


def update_status(acc, status, logged_in=True):
    try:
        db.collection(u'accounts').document(acc).update({u'status': status,
                                                     u'last_updated': datetime.datetime.now(),
                                                     u'logged_in': logged_in})
        return True
    except Exception as e:
        print(e)
        return False


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
