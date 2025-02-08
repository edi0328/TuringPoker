#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
from tg.types import *
import time

parser = argparse.ArgumentParser(
    prog='Template bot',
    description='A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)')

parser.add_argument('--port', type=int, default=1999,
                    help='The port to connect to the server on')
parser.add_argument('--host', type=str, default='localhost',
                    help='The host to connect to the server on')
parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')

args = parser.parse_args()

cnt = 0
# Always call
class TemplateBot(Bot):
    def act(self, state, my_cards):
        print('asked to act')
        print('acting', state, my_cards, self.my_id)

        me = self._find_me(state.players)
        if not me:
            # If we can’t find our player record, just call as a fallback
            return {'type': ActionType.CALL.value}

        call_amount = state.target_bet - me.current_bet

        # If the call requires more chips than we have, decide all-in or fold
        if call_amount >= me.stack:
            return self._decide_all_in_or_fold(my_cards)

        # Example: If we hold a pair >= 8, raise;
        # else if it's cheap, call; otherwise fold.
        if self._is_pair_of_eights_or_better(my_cards):
            raise_amount = max(call_amount * 2, 50)
            return {'type': ActionType.RAISE.value, 'amount': raise_amount}
        else:
            # If it's cheap, call; else fold
            if call_amount <= 50:
                return {'type': ActionType.CALL.value}
            else:
                return {'type': ActionType.FOLD.value}

    def _decide_all_in_or_fold(self, my_cards):
        if self._is_pair_of_eights_or_better(my_cards):
            # All-in by calling (since we don't have enough to just call)
            return {'type': ActionType.CALL.value}
        return {'type': ActionType.FOLD.value}

    def _is_pair_of_eights_or_better(self, my_cards):
        c1, c2 = my_cards[0], my_cards[1]
        if c1.rank == c2.rank and c1.rank >= Rank.EIGHT:
            return True
        return False

    def _find_me(self, players):
        for p in players:
            if p.id == self.my_id:
                return p
        return None

    def opponent_action(self, action, player):
        #print('opponent action?', action, player)
        pass

    def game_over(self, payouts):
        global cnt
        #print('game over', payouts)
        cnt += 1
        print(cnt)

    def start_game(self, my_id):
        self.my_id = my_id
        pass

if __name__ == "__main__":
    bot = TemplateBot(args.host, args.port, args.room, args.username)
    asyncio.run(bot.start())
