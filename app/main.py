from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastui.forms import SelectSearchResponse, fastui_form
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field

from app.dependencies.nascar import get_full_race_schedule_model, get_race_drivers, DriverSelectForm

app = FastAPI()


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
async def get_schedule() -> list[AnyComponent]:
    """Get NASCAR Schedule"""
    schedule = get_full_race_schedule_model()
    return [ 
        c.Page(
            components=[
                c.Heading(text='Schedule', level=2),
                c.Table(
                    data=schedule,
                    columns=[
                        DisplayLookup(field='track_name', on_click=GoToEvent(url='/races/{race_id}/')),
                        # the second is the date of birth, rendered as a date
                        DisplayLookup(field='start_time_utc', mode=DisplayMode.date),
                    ],
                ),
            ]
        ),
    ]


@app.get("/api/races/{race_id}/", response_model=FastUI, response_model_exclude_none=True)
def form_content(race_id, initial={}): #{ 'search_select_multiple': [{"value": "221202", "label": "Kyle Benjamin"}, '374531', '219299']}
    
    class CurrentRaceDrivers(BaseModel):
        search_select_multiple: list[str] = Field(title="Select 3 Drivers", description="drivers desc", json_schema_extra={'search_url': f'/api/races/{race_id}/drivers/'})

    return [
        c.Heading(text='Select Drivers', level=2),
        c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
        c.ModelForm(initial=initial, model=CurrentRaceDrivers, submit_url='/drivers/select'),
    ]


@app.post('/drivers/select', response_model=FastUI, response_model_exclude_none=True)
async def select_form_post(form: Annotated[DriverSelectForm, fastui_form(DriverSelectForm)]):
    print(form)
    return [c.FireEvent(event=GoToEvent(url='/'), message="Thank you for your picks!!")]


@app.get("/api/races/{race_id}/drivers/", response_model=SelectSearchResponse)
def user_profile(race_id: int) -> SelectSearchResponse:
    """
    User profile page, the frontend will fetch this when the user visits `/user/{id}/`.
    """
    #race = get_full_race_schedule_model(race_id)
    drivers = get_race_drivers(race_id)
    all_drivers = [{'label': driver.driver_name, 'value': str(driver.driver_id)} for driver in drivers]
    all_drivers_options = [
        {
            'label': 'Drivers',
            'options': all_drivers
        }
    ]
    return SelectSearchResponse(options=all_drivers_options)


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='FastUI Demo'))
