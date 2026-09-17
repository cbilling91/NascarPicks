import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.dependencies.nascar import (
    get_driver_points, calculate_points, is_playoff_race, has_race_started,
    assign_playoff_points, calculate_position_points, calculate_stage_points,
    publish_driver_picks, publish_driver_picks_relational
)
from app.models.nascar import LapTimes, PicksItem, PlayerPicks, StagePoints, DriverPoints, PickPoints, Driver, DriverSelectForm, Player, StagePointsItem, Result


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
        self.assertEqual(points, (10, 1))


    @patch('app.dependencies.nascar.RELATIONAL_CONNECTION_STRING', 'postgresql://test')
    @patch('app.dependencies.nascar.get_player')
    @patch('app.dependencies.nascar.psycopg2')
    @patch('app.dependencies.nascar.dapr_client')
    def test_publish_driver_picks_writes_both_formats(self, mock_dapr, mock_psycopg2, mock_get_player):
        # Mock data
        mock_get_player.return_value = Player(
            hash='abc123',
            id='player-chase-billing-9734765941',
            name='Chase Billing',
            phone_number='9734765941',
            type='player',
            admin=False
        )
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            '8ba427e0-d977-444d-a026-b20ab08c9720',)
        mock_psycopg2.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        form = DriverSelectForm(search_select_multiple=['4030', '1361', '4153'])

        # Call function
        publish_driver_picks('player-chase-billing-9734765941', '5386', form)

        # Old format: JSON document written to the Dapr state store
        mock_dapr.save_state.assert_called_once()
        dapr_args = mock_dapr.save_state.call_args
        self.assertEqual(
            dapr_args.args[1], 'picks-player-chase-billing-9734765941-5386')
        dapr_payload = json.loads(dapr_args.kwargs['value'])
        self.assertEqual(dapr_payload['type'], 'picks')
        self.assertEqual(dapr_payload['player'],
                         'player-chase-billing-9734765941')
        self.assertEqual(dapr_payload['race'], '5386')
        self.assertEqual(dapr_payload['picks'], ['4030', '1361', '4153'])

        # New format: profile looked up by phone number, then upserted row
        executed_sql = [call.args[0]
                        for call in mock_cursor.execute.call_args_list]
        self.assertIn('SELECT id FROM profiles WHERE phone_number = %s',
                      executed_sql[0])
        self.assertTrue(any('INSERT INTO picks' in sql for sql in executed_sql))
        insert_call = mock_cursor.execute.call_args_list[-1]
        self.assertEqual(
            insert_call.args[1],
            ('8ba427e0-d977-444d-a026-b20ab08c9720', 5386, 4030, 1361, 4153)
        )

    @patch('app.dependencies.nascar.RELATIONAL_CONNECTION_STRING', 'postgresql://test')
    @patch('app.dependencies.nascar.get_player')
    @patch('app.dependencies.nascar.psycopg2')
    @patch('app.dependencies.nascar.dapr_client')
    def test_publish_driver_picks_admin_player_select_writes_both_formats(self, mock_dapr, mock_psycopg2, mock_get_player):
        # Admin picking for another player should use the selected player
        mock_get_player.return_value = Player(
            hash='def456',
            id='player-don-9739197737',
            name='Don',
            phone_number='9739197737',
            type='player',
            admin=False
        )
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            'b11e6dce-96a0-44f5-936b-ded3f58ea509',)
        mock_psycopg2.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        form = DriverSelectForm(
            player_select='player-don-9739197737',
            search_select_multiple=['4030', '1361', '4153']
        )

        # Call function as an admin
        publish_driver_picks('player-chase-billing-9734765941', '5386', form)

        # Old format uses the selected player in the key and payload
        mock_dapr.save_state.assert_called_once()
        dapr_args = mock_dapr.save_state.call_args
        self.assertEqual(dapr_args.args[1], 'picks-player-don-9739197737-5386')
        dapr_payload = json.loads(dapr_args.kwargs['value'])
        self.assertEqual(dapr_payload['player'], 'player-don-9739197737')

        # New format is written for the selected player's profile
        insert_call = mock_cursor.execute.call_args_list[-1]
        self.assertEqual(
            insert_call.args[1],
            ('b11e6dce-96a0-44f5-936b-ded3f58ea509', 5386, 4030, 1361, 4153)
        )

    @patch('app.dependencies.nascar.RELATIONAL_CONNECTION_STRING', 'postgresql://test')
    @patch('app.dependencies.nascar.get_player')
    @patch('app.dependencies.nascar.psycopg2')
    @patch('app.dependencies.nascar.dapr_client')
    def test_publish_driver_picks_relational_failure_does_not_break_old_format(self, mock_dapr, mock_psycopg2, mock_get_player):
        # New format write failing must not prevent the old format write
        mock_psycopg2.connect.side_effect = Exception('connection refused')

        form = DriverSelectForm(search_select_multiple=['4030', '1361', '4153'])

        # Call function
        publish_driver_picks('player-chase-billing-9734765941', '5386', form)

        # Old format write still happened
        mock_dapr.save_state.assert_called_once()

    @patch('app.dependencies.nascar.RELATIONAL_CONNECTION_STRING', 'postgresql://test')
    @patch('app.dependencies.nascar.get_player')
    @patch('app.dependencies.nascar.psycopg2')
    def test_publish_driver_picks_relational_skips_unknown_profile(self, mock_psycopg2, mock_get_player):
        # Players with no matching profile should be skipped, not crash
        mock_get_player.return_value = Player(
            hash='xyz789',
            id='player-nobody-9999999999',
            name='Nobody',
            phone_number='9999999999',
            type='player',
            admin=False
        )
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_psycopg2.connect.return_value.cursor.return_value.__enter__.return_value = mock_cursor

        form = DriverSelectForm(search_select_multiple=['4030', '1361', '4153'])

        # Call function
        publish_driver_picks_relational('player-nobody-9999999999', '5386', form)

        # No insert was attempted
        executed_sql = [call.args[0]
                        for call in mock_cursor.execute.call_args_list]
        self.assertFalse(any('INSERT INTO picks' in sql for sql in executed_sql))


if __name__ == '__main__':
    unittest.main()
