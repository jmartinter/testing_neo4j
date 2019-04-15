#!/usr/bin/python3

import random
import configparser

from neo4j import GraphDatabase


NUM_TEAMS = 5
NUM_CHANNELS = 20
NUM_FOLLOWERS = 100

MAX_FOLLOWED_CHANNELS = 8

COUNTRIES = ['US', 'Spain', 'FRANCE', 'GERMANY', 'CANADA']
AGES = [20, 30, 40, 50, 60]
GENDER = ['male', 'female']

random.seed(a=11111111)




def generate_teams(num_teams):
    for i in range(num_teams):
        yield {'id': 't{}'.format(i), 
               'name': 'Team {}'.format(i)}


def generate_channels(num_channels):
    for i in range(num_channels):
        team_id = random.randint(0, NUM_TEAMS)
        yield {'id': 'c{}_{}'.format(team_id, i), 
               'name': 'Channel {} on {}'.format(i, team_id), 
               'owned_by': 't{}'.format(team_id)}


def follower_demographics():
    demographics = {}
    if random.random() < 0.6:
        demographics['gender'] = random.choice(GENDER)
    if random.random() < 0.7:
        demographics['country'] = random.choice(COUNTRIES)
    if random.random() < 0.2:
        demographics['age'] = random.choice(AGES)
    return demographics


def generate_followers(num_followers):
    for i in range(num_followers):
        follower = follower_demographics()
        follower['id'] = 'f{}'.format(i)
        follower['name'] = 'Follower {}'.format(i)
        follower['relevance'] = random.randint(0, 99)
        yield follower


def delete_graph(tx):
    tx.run('MATCH (f) DETACH DELETE f')


def add_teams(tx, teams):
    # Runs in a single transaction
    # Avoids duplicates
    tx.run('UNWIND $teams as team '
	   'MERGE (t:Team {id: team.id}) '
           'ON CREATE SET t += team',
           teams=teams)


def add_channels(tx, channels):
    # Avoids duplicates
    tx.run('UNWIND $channels as channel '
           'MATCH (t:Team {id: channel.owned_by})'
           'MERGE (t)-[:OWNS]->(c:SocialChannel {id: channel.id})'
           'ON CREATE SET c += channel' , 
           channels=channels)


def add_followers(tx, followers):
    # Avoids duplicates
    tx.run('UNWIND $followers as follower '
           'MERGE (f:Follower {id: follower.id}) '
           'ON CREATE SET f += follower',
           followers=followers)


def add_follower_connections(tx, follower):
    # Avoids duplicates
    num_connections = random.randint(1, min(len(channels), MAX_FOLLOWED_CHANNELS))

    followed_channels = random.sample(channels, num_connections)
    tx.run('UNWIND $channels as channel '
           'MATCH (c:SocialChannel {id: channel.id}) '
           'MATCH (f:Follower {id: $f.id}) '
           'MERGE (c)<-[:FOLLOWS]-(f)',
           channels=followed_channels, f=follower)

    print('Follower {} follows {} channels'.format(follower['name'], num_connections))


if __name__ == '__main__':

    # Get configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_uri = config['DEFAULT']['db_uri']
    username = config['DEFAULT']['username']
    pwd = config['DEFAULT']['pwd']

    driver = GraphDatabase.driver(db_uri, auth=(username, pwd))

    with driver.session() as session:
        session.write_transaction(delete_graph)

        teams = list(generate_teams(NUM_TEAMS))
        session.write_transaction(add_teams, teams)

        channels = list(generate_channels(NUM_CHANNELS))
        session.write_transaction(add_channels, channels)

        followers = list(generate_followers(NUM_FOLLOWERS))
        session.write_transaction(add_followers, followers)
        for follower in followers:
            session.write_transaction(add_follower_connections, follower)



