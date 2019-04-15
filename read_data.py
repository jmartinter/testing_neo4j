from neo4j import GraphDatabase

# https://lime-louie-runolfsson-club.graphstory.link
db_uri = 'bolt://lime-louie-runolfsson-club.graphstory.link:7687'
username = 'lime_louie_runolfsson_club'
pwd = '2bRATRGdBZJRILwOZHFOflVfO7tXB'



driver = GraphDatabase.driver(db_uri, auth=(username, pwd))


def get_gender_demographics_for_channel(tx, channel_id):
    results = tx.run('MATCH (c:SocialChannel {id: $channel_id})<-[:FOLLOWS]-(f:Follower)'
		     'WHERE exists(f.gender)'
	             'RETURN f.gender AS Gender, count(f.gender) AS Count',
                     channel_id=channel_id)
    # results.records is a generator that returns neo4j.Record objects
    # https://neo4j.com/docs/driver-manual/1.7/cypher-values/#driver-result
    return results


channel_id = 'c11'
with driver.session() as session:
    results = session.write_transaction(get_gender_demographics_for_channel, channel_id)

data = results.data()
print data
'''
[{u'Count': 8, u'Gender': u'male'}, {u'Count': 2, u'Gender': u'female'}]
'''


