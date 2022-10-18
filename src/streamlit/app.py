import streamlit as st
import firebase_admin as fba
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
cred = credentials.Certificate("src/firebase_tools/runebot_key.json")
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
st.markdown('## <u>Active Players</u>', unsafe_allow_html=True)
active, inactive = get_player_statuses()
if len(active) > 0:
    active_cols = st.columns(len(active))
    for i, player in enumerate(active):
        active_cols[i].subheader(player['username'].title())
        active_cols[i].markdown(f"**Status:** {player['status']}")
        active_cols[i].markdown(f"**{player['action_update_type']}**: {player['action_value']}")
        active_cols[i].markdown(f"**Last Updated:** {player['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}")
        but = active_cols[i].button('Logout')
        if but:
            db.collection(u'accounts').document(player['username']).update({
                u'new_action': 'logout',
                u'last_updated': datetime.datetime.now()})
st.markdown('---')
st.markdown('## <u>Inactive Players</u>', unsafe_allow_html=True)
if len(inactive) > 0:
    inactive_cols = st.columns(len(inactive))
    for i, player in enumerate(inactive):
        inactive_cols[i].subheader(player['username'].title())
        inactive_cols[i].markdown(f"**Status:** {player['status']}")
        inactive_cols[i].markdown(f"**{player['action_update_type']}**: {player['action_value']}")
        inactive_cols[i].markdown(f"**Last Updated:** {player['last_updated']}")
st.markdown('---')
