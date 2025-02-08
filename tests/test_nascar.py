import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.dependencies.nascar import (
    get_driver_points, calculate_points, is_playoff_race, has_race_started,
    assign_playoff_points, calculate_position_points, calculate_stage_points
)
from app.models.nascar import LapTimes, PicksItem, PlayerPicks, StagePoints, DriverPoints, PickPoints, Driver, Player, StagePointsItem, Result


class TestNascarFunctions(unittest.TestCase):

    @patch('app.dependencies.nascar.get_player')
    @patch('app.dependencies.nascar.get_driver_picks')
    @patch('app.dependencies.nascar.get_full_race_schedule_model')
    @patch('app.dependencies.nascar.get_weekend_feed')
    @patch('app.dependencies.nascar.get_driver_position')
    @patch('app.dependencies.nascar.get_driver_stage_points')
    def test_get_driver_points(self, mock_stage_points, mock_position, mock_weekend_feed, mock_schedule, mock_picks, mock_get_player):
        # Mock data
        mock_player = MagicMock(spec=Player)
        mock_player.name = 'player1'
        mock_get_player.return_value = mock_player

        mock_driver = MagicMock(spec=Driver)
        mock_driver.Nascar_Driver_ID = 1
        mock_driver.Full_Name = 'Driver 1'

        mock_picks.return_value = [
            PicksItem(player='player1', picks=[mock_driver], race='Race 1', type='RaceType')
        ]
        mock_schedule.side_effect = lambda id=None: MagicMock(race_id=id, event_name='Race', race_name='DAYTONA 500') if id else [
            MagicMock(race_id='1', event_name='Race', race_name='DAYTONA 500'),
            MagicMock(race_id='2', event_name='Race', race_name='Race 2')
        ]
        mock_weekend_feed.return_value = MagicMock(weekend_race=[MagicMock(playoff_round=True)])
        mock_position.return_value = MagicMock(flags=[MagicMock(FlagState=1)])
        mock_stage_points.return_value = StagePoints(root=[])

        # Call function
        result = get_driver_points('1')

        # Assertions
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 0)

    def test_calculate_position_points(self):
        # Mock data
        mock_results = MagicMock(laps=[MagicMock(NASCARDriverID=1)])
        mock_pick = MagicMock(Nascar_Driver_ID=1)

        # Call function
        points = calculate_position_points(mock_results, mock_pick)

        # Assertions
        self.assertEqual(points, 40)

    def test_calculate_stage_points(self):
        # Mock data
        mock_result = MagicMock(spec=Result)
        mock_result.driver_id = 1
        mock_result.position = 1
        mock_result.stage_points = 10

        mock_stage_points = StagePoints(root=[StagePointsItem(race_id=1, run_id=1, stage_number=1, results=[mock_result])])
        mock_pick = MagicMock(spec=PickPoints)
        mock_pick.Nascar_Driver_ID = 1
        mock_pick.stage_points = 0
        mock_pick.stage_wins = 0

        # Call function
        points = calculate_stage_points(mock_stage_points, mock_pick)

        # Assertions
        self.assertEqual(points, 10)


if __name__ == '__main__':
    unittest.main()
