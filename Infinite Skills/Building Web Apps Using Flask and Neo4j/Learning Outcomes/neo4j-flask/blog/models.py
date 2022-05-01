from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid


graph = Graph()

class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.nodes.match("User", username=self.username).first()
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
