import streamlit as st
import firebase_admin as fba
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("src/firebase/runebot_key.json")
try:
    fba.initialize_app(cred)
except ValueError:
    pass
db = fba.firestore.client()


def get_player_statuses():
    # get main bot data
    docs = db.collection(u'accounts').stream()
    active, inactive = [], []
    for doc in docs:
        if doc.exists:
            player = doc.to_dict()
            if player['logged_in']:
                active.append(player)
            else:
                inactive.append(player)
    return active, inactive

st.title("RuneScape Scheduler")
st.markdown('---')
active, inactive = get_player_statuses()
if len(active) > 0:
    active_cols = st.columns(len(active))
    for i, player in enumerate(active):
        active_cols[i].subheader(player['username'])
        active_cols[i].markdown(f"**Status:** {player['status']}")
        active_cols[i].markdown(f"**Last Updated:** {player['last_updated']}")
        active_cols[i].markdown(f"**Sub Action:** {player['sub_action']}")
st.markdown('---')
if len(inactive) > 0:
    inactive_cols = st.columns(len(inactive))
    for i, player in enumerate(inactive):
        inactive_cols[i].subheader(player['username'])
        inactive_cols[i].markdown(f"**Status:** {player['status']}")
        inactive_cols[i].markdown(f"**Last Updated:** {player['last_updated']}")
        inactive_cols[i].markdown(f"**Sub Action:** {player['sub_action']}")
st.markdown('---')
