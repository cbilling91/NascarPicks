from typing import Annotated
import time

from fastapi import FastAPI, Depends, Response
from fastapi.responses import HTMLResponse
from fastui.forms import SelectSearchResponse, fastui_form
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field

from app.dependencies.nascar import *
from app.models.nascar import DriverSelectForm, UserForm, Player

app = FastAPI()


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def get_schedule(player: Player = Depends(get_player_interface)) -> list[AnyComponent]:
    """Get NASCAR Schedule"""
    schedule = get_full_race_schedule_model()
    return [
        c.Page(
            components=[
                c.LinkList(
                    links=[
                        c.Link(
                            components=[c.Text(text='Manage Users')],
                            on_click=GoToEvent(url='/users/'),
                        )
                    ],
                ),
                c.Heading(text='Schedule', level=2),
                c.Table(
                    data=schedule,
                    columns=[
                        DisplayLookup(field='track_name'),
                        DisplayLookup(field='race_name'),
                        # the second is the date of birth, rendered as a date
                        DisplayLookup(field='start_time_utc',
                                      mode=DisplayMode.date),
                        DisplayLookup(field='picks', on_click=GoToEvent(
                            url='/picks/{race_id}/')),
                        DisplayLookup(field='race', on_click=GoToEvent(
                            url='/races/{race_id}/')),
                    ],
                ),
            ]
        ),
    ]


@app.get("/api/picks/{race_id}/", response_model=FastUI, response_model_exclude_none=True)
def form_content(race_id: str, player: Player = Depends(get_player_interface)):
    if type(player) == Response:
        return player
    current_picks = get_driver_picks(player.id, race_id)
    current_race = get_full_race_schedule_model(race_id)
    print(current_picks)

    class CurrentRaceDrivers(BaseModel):
        search_select_multiple: list[str] = Field(title="Select 3 Drivers", description="drivers desc", json_schema_extra={
                                                  'search_url': f'/api/races/{race_id}/drivers/'})
    components = [
        c.Link(
            components=[c.Text(text='Back to Schedule')],
            
            on_click=GoToEvent(url='/'),
        ),
        c.Heading(text=f"Hello {player.name.split()[0]}", level=1),
        c.Heading(text=f"{current_race.track_name} - {current_race.race_name}", level=3),
    ]
    if current_picks:
        components += [
            c.Table(
                data=current_picks,
                columns=[
                    DisplayLookup(field='Full_Name'),
                    DisplayLookup(field='Badge'),
                    DisplayLookup(field='Team')
                ],
            )
        ]
    else:
        components += [
            c.Heading(text='Make Your Picks', level=3)
        ]
    components += [c.ModelForm(model=CurrentRaceDrivers,
                               submit_url=f'/api/picks/{race_id}/')]
    return [
        c.Page(
            components=components
        )
    ]


@app.post('/api/picks/{race_id}/', response_model=FastUI, response_model_exclude_none=True)
async def select_form_post(race_id: str, form: Annotated[DriverSelectForm, fastui_form(DriverSelectForm)], player: Player = Depends(get_player_interface)):
    publish_driver_picks(player.id, race_id, form.search_select_multiple)
    return [c.FireEvent(event=GoToEvent(url=f'/thanks/{race_id}/'), message="Thank you for your picks!!")]


@app.get("/api/thanks/{race_id}/", response_model=FastUI, response_model_exclude_none=True)
def thanks(race_id: str, player: Player = Depends(get_player_interface)):
    return [c.FireEvent(event=GoToEvent(url=f'/picks/{race_id}/', message="Thank you for your picks!!"))]


@app.get("/api/races/{race_id}/", response_model=FastUI, response_model_exclude_none=True)
def user_profile(race_id: int, player: Player = Depends(get_player_interface)):
    """
    User profile page, the frontend will fetch this when the user visits `/user/{id}/`.
    """
    #results = get_results(race_id)
    results = get_driver_position(race_id)
    driver_points = get_driver_points(race_id)

    components = []
    components += [
                c.Link(
                    components=[c.Text(text='Back to Schedule')],
                    on_click=GoToEvent(url='/'),
                ),
                c.Heading(text='Picks', level=2),
            ]
    if driver_points:
        components += [
                c.Table(
                    data=driver_points,
                    columns=[
                        DisplayLookup(field='name'),
                        DisplayLookup(field='pick_1'),
                        DisplayLookup(field='pick_2'),
                        DisplayLookup(field='pick_3'),
                        DisplayLookup(field='points')
                    ]
                )
            ]
    else:
        components += [
            c.Text(text="No picks made yet.")
        ]

    components += [ c.Heading(text='Race', level=2) ]
    
    if results:
        components += [
            
            c.Table(
                data=results,
                columns=[
                    DisplayLookup(field='RunningPos'),
                    DisplayLookup(field='FullName')
                ],
            )
        ]
    else:
        components += [
            c.Text(text="Race has not started.")
        ]

    # DisplayLookup(field='position'),
    # DisplayLookup(field='driver_fullname'),
    # DisplayLookup(field='points_earned'),
    # DisplayLookup(field='qualifying_position'),
    # DisplayLookup(field='team_name')

    return [
        c.Page(
            components=components
        )
    ]


@app.get("/api/races/{race_id}/drivers/", response_model=SelectSearchResponse)
def user_profile(race_id: int, player: Player = Depends(get_player_interface)) -> SelectSearchResponse:
    """
    User profile page, the frontend will fetch this when the user visits `/user/{id}/`.
    """
    return get_all_cup_drivers_pick_options()


@app.get("/api/users/", response_model=FastUI, response_model_exclude_none=True)
def user_form(player: str = Depends(check_admin_user)):
    return [
        c.Page(
            components=[
                c.Link(
                    components=[c.Text(text='Back to Schedule')],
                    on_click=GoToEvent(url='/'),
                ),
                c.Heading(text='User Form', level=2),
                c.Paragraph(text='Simple login form with email and password.'),
                c.ModelForm(model=UserForm, submit_url='/api/users/create/'),
            ]
        )
    ]


@app.post("/api/users/create/", response_model=FastUI, response_model_exclude_none=True)
def manage_users(form: Annotated[UserForm, fastui_form(UserForm)], player: Player = Depends(get_player_interface)):
    publish_user(form)
    return [c.FireEvent(event=GoToEvent(url='/'))]


@app.get('/{path:path}')
async def html_landing(player: Player = Depends(get_player_interface)) -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='FastUI Demo'))
