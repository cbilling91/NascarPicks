import streamlit as st
from datetime import datetime, UTC
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import Response

from app.dependencies.nascar import (
    check_admin_user, 
    get_player_interface, 
    get_driver_picks, 
    get_full_race_schedule_model,
    race_started,
    get_driver_position,
    get_driver_points, 
    get_players, 
    get_all_cup_drivers_pick_options, 
    publish_driver_picks, 
    publish_user,
    delete_player
)
from app.models.nascar import DriverSelectForm, UserForm, Player

st.set_page_config(page_title="NASCAR Picks", layout="wide")

def get_schedule():
    query_params = st.experimental_get_query_params()
    player_id = query_params.get('player_id', [None])[0]  # Get player_id from query params
    player = get_player_interface(player_id)
    schedule = get_full_race_schedule_model(one_week_in_future_only=True)
    return player, schedule

def display_schedule():
    player, schedule = get_schedule()
    st.title(f"Welcome {player.name}")
    st.header("Upcoming Races")
    
    # Create a list to hold table data
    table_data = []
    
    for event in schedule:
        table_data.append({
            "Track": event.track_name,
            "Race": event.race_name,
            "Make Picks": st.button("Make Picks", key=f"make_picks_{event.race_id}"),
            "Race": st.button("Race", key=f"race_{event.race_id}")
        })
    
    # Display the table
    df = st.dataframe(table_data)
    
    # # Create columns for buttons
    # col1, col2, col3, col4 = st.columns(4)
    
    # for i, event in enumerate(schedule):
    #     with col1:
    #         st.write(event.track_name)
    #     with col2:
    #         st.write(event.race_name)
    #     with col3:
    #         if st.button("Make Picks", key=f"make_picks_{event.race_id}"):
    #             form_content(event.race_id)
    #     with col4:
    #         if st.button("Race", key=f"race_{event.race_id}"):
    #             pass  # Add functionality for the "Race" button

def form_content(race_id):
    query_params = st.experimental_get_query_params()
    player_id = query_params.get('player_id', [None])[0]  # Get player_id from query params
    player = get_player_interface(player_id)
    current_picks = get_driver_picks(race_id, player.id)
    current_race = get_full_race_schedule_model(int(race_id))
    started = race_started(race_id)

    if not started or player.admin:
        class CurrentRaceDrivers(BaseModel):
            if player.admin:
                player_select: str = Field(title="Player", default=player.id, description="Leave blank to pick as you")
            search_select_multiple: list[str] = Field(title="Select 3 Drivers", description="drivers desc")

        if current_picks.root:
            st.write("Current Picks:")
            st.write(current_picks.root[0].picks)
        else:
            st.write("Make Your Picks")

        form = CurrentRaceDrivers()
        st.form(key="my_form")
        st.write("Player:")
        player_select = st.selectbox("Player", [player.id])
        st.write("Select 3 Drivers:")
        search_select_multiple = st.multiselect("Select 3 Drivers", get_all_cup_drivers_pick_options(""))
        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            publish_driver_picks(player.id, race_id, DriverSelectForm(search_select_multiple=search_select_multiple))

    else:
        st.write("Race has already started. No more picks can be made.")

def user_profile():
    players = get_players()
    st.title("Users")
    st.write(players)

def user_form():
    players = get_players()
    st.title("User Form")
    form = UserForm()
    st.write("Name:")
    name = st.text_input("Name")
    st.write("Phone Number:")
    phone_number = st.text_input("Phone Number")
    st.write("Text Notifications:")
    text_notifications = st.checkbox("Text Notifications")
    st.write("Admin:")
    admin = st.checkbox("Admin")
    submit_button = st.button("Submit")

    if submit_button:
        publish_user(UserForm(name=name, phone_number=phone_number, text_notifications=text_notifications, admin=admin))

def delete_user_confirm(user_id):
    players = get_players()
    user_to_delete = next((player for player in players if player.id == user_id), None)
    if not user_to_delete:
        st.write("User not found")
    else:
        st.write(f"Are you sure you want to delete user '{user_to_delete.name}'?")
        delete_button = st.button("Delete")
        if delete_button:
            delete_player(user_id)
            st.write("User deleted")

def main():
    display_schedule()
    st.write("Select a page:")
    page = st.selectbox("Page", ["Schedule", "Picks", "Users", "User Form", "Delete User"])
    if page == "Picks":
        race_id = st.text_input("Enter race ID")
        form_content(race_id)
    elif page == "Users":
        user_profile()
    elif page == "User Form":
        user_form()
    elif page == "Delete User":
        user_id = st.text_input("Enter user ID")
        delete_user_confirm(user_id)

if __name__ == "__main__":
    main()
