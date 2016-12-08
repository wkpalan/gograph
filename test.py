#!/usr/bin/env python

from go_utils import obo
from neo4j.v1 import GraphDatabase, basic_auth, CypherError, ResultError
import pprint
import json

driver = GraphDatabase.driver("bolt://172.17.0.2", auth=basic_auth("neo4j", "bot566466"))
session = driver.session()

x = obo()
x.read_file("go.obo")
pp = pprint.PrettyPrinter(indent=4)


def addNodeToDb(term):
    results = session.run("MATCH (n:GO) WHERE n.id = {id} RETURN n", {"id": term['id']})
    try:
            print results.peek()
    except CypherError:
         print ("Node not found so adding it")
         session.run("CREATE (n:GO {id: {id},name:{name}})", {"id": term['id'],"name":term['name']})
    except ResultError:
        print ("Node not found so adding it")
        session.run("CREATE (n:GO {id: {id},name:{name}})", {"id": term['id'],"name":term['name']})
    return True

def addRelationship(endId,relType,startId):
    print "%s -[%s]-> %s" % (endId,relType,startId)
    nodeType="GO"
    results = session.run("MERGE (a:%s {id:{startId}}) MERGE (b:%s {id:{endId}}) MERGE (a)-[r:%s]->(b)"
     % (nodeType,nodeType,relType), {"startId": startId,"endId":endId})
    results.consume()

def addNodeProperties(term):
    id = term["id"]
    print "Adding %s properties" % (id)
    results = session.run("MATCH (a:GO {id:{map}.id}) SET a += {map}", {"map": term})
    results.consume()

def addNode(term):
    id = term["id"]
    results = session.run("MERGE (a:GO {id:{map}.id}) SET a += {map}", {"map": term})
    results.consume()

for term in x.terms:
    #print term
    if "is_obsolete" not in term:
        #
        if 'is_a' in term:
            for parent in term['is_a']:
                addRelationship(term["id"],"is_a",parent)
        else:
            #pp.pprint(term)
            addNode(term)

        if 'relationship' in term:
            for relationship in  term["relationship"]:
                parts = relationship.split(" ")
                addRelationship(term["id"],parts[0],parts[1])
        #pp.pprint(term)
        addNodeProperties(term)
