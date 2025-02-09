#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
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
def checkFlush(hand, community):
    cards = list(hand) + list(community)
    if len(cards) < 5:
        return False
    suitCount = {'hearts' : 0,
                 'diamonds' : 0,
                 'clubs' : 0,
                 'spades' : 0,}
    for card in cards:
        suit = card.suit.value
        suitCount[suit] += 1
        if suitCount[suit] >= 5:
            return True
    return False


def checkStraight(hand, community):
    cards = list(hand) + list(community)
    if len(cards) < 5:
        return False
    cards.sort(key=lambda card: card.rank.value)
    length = 1
    for i in range(1, len(cards)):
        if cards[i] - 1 != cards[i]:
            length += 1
            if length >= 5:
                return True
        else:
            length = 1
    return False

def findPairs(hand, community):
    """
    :param hand: 2 cards dealt
    :param community: cards shared
    :return: number of doubles, triples and quadruples possible
    """
    rankCount = [0] * 15
    cards = list(hand) + list(community)
    doubles = 0
    triples = 0
    quadruples = 0
    for card in cards:
        curRank = card.rank.value
        rankCount[curRank] += 1
        if rankCount[curRank] == 2:
            doubles += 1
        elif rankCount[curRank] == 3:
            triples += 1
            doubles -= 1
        elif rankCount[curRank] == 4:
            quadruples += 1
            triples -= 1

    return (doubles, triples, quadruples)

class TemplateBot(Bot):
    def act(self, state, hand):
        print('asked to act')
        print('acting', state, hand, self.my_id)
        return {'type': 'call'}
    """
    when pre-flop:
        
    """

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
