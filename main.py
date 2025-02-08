#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
from tg.types import *
import time
import random
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
    def __init__(self, host, port, room, username):
        super().__init__(host, port, room, username)
        self.my_id = None
        self.opponent_counters = {}
        random.seed(time.time())

    def start_game(self, my_id):
        self.my_id = my_id

    def opponent_action(self, action, player):
        if player.id == self.my_id:
            return
        pid = player.id
        if pid not in self.opponent_counters:
            self.opponent_counters[pid] = {'folds': 0, 'calls': 0, 'raises': 0, 'hands': 0}
        if action.type == ActionType.FOLD:
            self.opponent_counters[pid]['folds'] += 1
        elif action.type == ActionType.CALL:
            self.opponent_counters[pid]['calls'] += 1
        elif action.type == ActionType.RAISE:
            self.opponent_counters[pid]['raises'] += 1

    def game_over(self, payouts):
        global cnt
        cnt += 1
        print(f"Game over #{cnt}. Payouts: {payouts}")
        if payouts:
            for pid in payouts:
                if pid in self.opponent_counters:
                    self.opponent_counters[pid]['hands'] += 1

    def act(self, state: PokerSharedState, hand):
        me = self._find_me(state.players)
        if not me:
            return {'type': ActionType.CALL.value}
        call_amount = state.target_bet - me.current_bet
        if call_amount >= me.stack:
            return self._decide_all_in_or_fold(hand, state.round)
        preflop_score = self._preflop_rating(hand)
        table_tendency = self._read_table_style(state.players)
        if state.round == PokerRound.PRE_FLOP:
            return self._preflop_action(preflop_score, call_amount)
        else:
            return self._postflop_action(state, hand, preflop_score, call_amount, table_tendency)

    def _decide_all_in_or_fold(self, hand, current_round):
        score = self._preflop_rating(hand)
        if score >= 0.3 or current_round != PokerRound.PRE_FLOP:
            return {'type': ActionType.CALL.value}
        return {'type': ActionType.FOLD.value}

    def _preflop_rating(self, cards):
        if len(cards) != 2:
            return 0.0
        c1, c2 = cards
        r1 = 14 if c1.rank == Rank.ACE else c1.rank
        r2 = 14 if c2.rank == Rank.ACE else c2.rank
        if r1 > r2:
            r1, r2 = r2, r1
        if c1.rank == c2.rank:
            return 0.4 + 0.6 * (r1 - 2) / 12.0
        suited_bonus = 0.04 if c1.suit == c2.suit else 0.0
        if r1 >= 10:
            base_score = 0.7 + suited_bonus
        elif r1 >= 8 and r2 >= 10:
            base_score = 0.5 + suited_bonus
        else:
            base_score = 0.3 + suited_bonus * 2
        gap_penalty = min((r2 - r1) * 0.03, 0.3)
        return max(0.0, min(1.0, base_score - gap_penalty))

    def _preflop_action(self, score, call_amount):
        if score > 0.8:
            raise_size = max(int(call_amount * (2 + random.random())), 40)
            return {'type': ActionType.RAISE.value, 'amount': raise_size}
        elif score < 0.2 and call_amount > 0:
            return {'type': ActionType.FOLD.value}
        return {'type': ActionType.CALL.value}

    def _postflop_action(self, state, hand, preflop_score, call_amount, table_tendency):
        if not state.cards:
            return self._preflop_action(preflop_score, call_amount)
        matched = self._board_match(state.cards, hand)
        if matched or preflop_score > 0.7:
            if table_tendency == 'folds_often':
                bet_amount = max(int(call_amount * (2 + random.random())), 80)
                return {'type': ActionType.RAISE.value, 'amount': bet_amount}
            else:
                if call_amount <= 100:
                    raise_amt = max(int(call_amount * (1.5 + random.random())), 60)
                    return {'type': ActionType.RAISE.value, 'amount': raise_amt}
                return {'type': ActionType.CALL.value}
        else:
            if call_amount > 100:
                return {'type': ActionType.FOLD.value}
            if table_tendency == 'folds_often' and random.random() < 0.3:
                bluff_amt = max(60, call_amount * 2)
                return {'type': ActionType.RAISE.value, 'amount': bluff_amt}
            return {'type': ActionType.CALL.value}

    def _board_match(self, board_cards, hole_cards):
        board_ranks = [c.rank for c in board_cards]
        for card in hole_cards:
            if card.rank in board_ranks:
                return True
        return False

    def _read_table_style(self, players):
        total_folds = 0
        total_calls = 0
        total_raises = 0
        total_hands = 0
        for p in players:
            if p.id == self.my_id or p.folded:
                continue
            if p.id not in self.opponent_counters:
                continue
            s = self.opponent_counters[p.id]
            total_folds += s['folds']
            total_calls += s['calls']
            total_raises += s['raises']
            total_hands += s['hands']
        if total_hands < 1:
            return 'normal'
        fold_ratio = total_folds / total_hands
        call_ratio = total_calls / total_hands
        raise_ratio = total_raises / total_hands
        if fold_ratio > 0.5:
            return 'folds_often'
        elif call_ratio > 0.5:
            return 'calls_often'
        elif raise_ratio > 0.3:
            return 'raises_often'
        return 'normal'

    def _find_me(self, players):
        for p in players:
            if p.id == self.my_id:
                return p
        return None

if __name__ == "__main__":
    bot = TemplateBot(args.host, args.port, args.room, args.username)
    asyncio.run(bot.start())
