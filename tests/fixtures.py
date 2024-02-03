import json

from app.models.nascar import WeekendFeed

drivers = {
    "response": [
        {
            "Nascar_Driver_ID": 1,
            "Driver_ID": 1,
            "Driver_Series": "Cup",
            "First_Name": "Cup",
            "Last_Name": "Last ",
            "Full_Name": "Cup Last",
            "Series_Logo": "https://www.nascar.com/wp-content/uploads/sites/1/1111/11/11/series.svg",
            "Short_Name": "",
            "Description": "",
            "DOB": "",
            "DOD": "0001-01-01T00:00:00",
            "Hometown_City": "",
            "Crew_Chief": "Guy",
            "Hometown_State": "",
            "Hometown_Country": "",
            "Rookie_Year_Series_1": 0,
            "Rookie_Year_Series_2": 0,
            "Rookie_Year_Series_3": 0,
            "Hobbies": "",
            "Children": "",
            "Twitter_Handle": "",
            "Residing_City": "",
            "Residing_State": "",
            "Residing_Country": "",
            "Badge": "4237",
            "Badge_Image": "https://cf.nascar.com/data/images/carbadges/1/1111.png",
            "Manufacturer": "",
            "Manufacturer_Small": "",
            "Team": "4237",
            "Image": "https://www.nascar.com/wp-includes/images/media/default.png",
            "Image_Small": "",
            "Image_Transparent": "",
            "SecondaryImage": "",
            "Firesuit_Image": "",
            "Firesuit_Image_Small": "",
            "Career_Stats": "",
            "Driver_Page": "",
            "Age": 0,
            "Rank": "0",
            "Points": "0",
            "Points_Behind": 0,
            "No_Wins": "0",
            "Poles": "0",
            "Top5": "0",
            "Top10": "0",
            "Laps_Led": "0",
            "Stage_Wins": "0",
            "Playoff_Points": "0",
            "Playoff_Rank": "0",
            "Integrated_Sponsor_Name": "",
            "Integrated_Sponsor": "",
            "Integrated_Sponsor_URL": "",
            "Silly_Season_Change": "",
            "Silly_Season_Change_Description": ""
        },
        {
            "Nascar_Driver_ID": 3,
            "Driver_ID": 3,
            "Driver_Series": "Truck",
            "First_Name": "Truck",
            "Last_Name": "Last ",
            "Full_Name": "Truck Last",
            "Series_Logo": "https://www.nascar.com/wp-content/uploads/sites/1/1111/11/11/series.svg",
            "Short_Name": "",
            "Description": "",
            "DOB": "",
            "DOD": "0001-01-01T00:00:00",
            "Hometown_City": "",
            "Crew_Chief": "Guy 3",
            "Hometown_State": "",
            "Hometown_Country": "",
            "Rookie_Year_Series_1": 0,
            "Rookie_Year_Series_2": 0,
            "Rookie_Year_Series_3": 0,
            "Hobbies": "",
            "Children": "",
            "Twitter_Handle": "",
            "Residing_City": "",
            "Residing_State": "",
            "Residing_Country": "",
            "Badge": "4237",
            "Badge_Image": "https://cf.nascar.com/data/images/carbadges/1/1111.png",
            "Manufacturer": "",
            "Manufacturer_Small": "",
            "Team": "4237",
            "Image": "https://www.nascar.com/wp-includes/images/media/default.png",
            "Image_Small": "",
            "Image_Transparent": "",
            "SecondaryImage": "",
            "Firesuit_Image": "",
            "Firesuit_Image_Small": "",
            "Career_Stats": "",
            "Driver_Page": "",
            "Age": 0,
            "Rank": "0",
            "Points": "0",
            "Points_Behind": 0,
            "No_Wins": "0",
            "Poles": "0",
            "Top5": "0",
            "Top10": "0",
            "Laps_Led": "0",
            "Stage_Wins": "0",
            "Playoff_Points": "0",
            "Playoff_Rank": "0",
            "Integrated_Sponsor_Name": "",
            "Integrated_Sponsor": "",
            "Integrated_Sponsor_URL": "",
            "Silly_Season_Change": "",
            "Silly_Season_Change_Description": ""
        },
        {
            "Nascar_Driver_ID": 2,
            "Driver_ID": 2,
            "Driver_Series": "Xfinity",
            "First_Name": "Xfinity",
            "Last_Name": "Last ",
            "Full_Name": "Xfinity Last",
            "Series_Logo": "https://www.nascar.com/wp-content/uploads/sites/1/1111/11/11/series.svg",
            "Short_Name": "",
            "Description": "",
            "DOB": "",
            "DOD": "0001-01-01T00:00:00",
            "Hometown_City": "",
            "Crew_Chief": "Guy 2",
            "Hometown_State": "",
            "Hometown_Country": "",
            "Rookie_Year_Series_1": 0,
            "Rookie_Year_Series_2": 0,
            "Rookie_Year_Series_3": 0,
            "Hobbies": "",
            "Children": "",
            "Twitter_Handle": "",
            "Residing_City": "",
            "Residing_State": "",
            "Residing_Country": "",
            "Badge": "4237",
            "Badge_Image": "https://cf.nascar.com/data/images/carbadges/1/1111.png",
            "Manufacturer": "",
            "Manufacturer_Small": "",
            "Team": "4237",
            "Image": "https://www.nascar.com/wp-includes/images/media/default.png",
            "Image_Small": "",
            "Image_Transparent": "",
            "SecondaryImage": "",
            "Firesuit_Image": "",
            "Firesuit_Image_Small": "",
            "Career_Stats": "",
            "Driver_Page": "",
            "Age": 0,
            "Rank": "0",
            "Points": "0",
            "Points_Behind": 0,
            "No_Wins": "0",
            "Poles": "0",
            "Top5": "0",
            "Top10": "0",
            "Laps_Led": "0",
            "Stage_Wins": "0",
            "Playoff_Points": "0",
            "Playoff_Rank": "0",
            "Integrated_Sponsor_Name": "",
            "Integrated_Sponsor": "",
            "Integrated_Sponsor_URL": "",
            "Silly_Season_Change": "",
            "Silly_Season_Change_Description": ""
        }
    ]
}

with open('examples/results.json', 'r') as file:
    results = json.load(file)

results_model = WeekendFeed(**results)