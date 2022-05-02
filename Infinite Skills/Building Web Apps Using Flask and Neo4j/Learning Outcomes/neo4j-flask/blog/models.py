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
            graph.create(user)
            return True

        return False

    def verify_password(self, password):
        user = self.find()

        if not user:
            return False

        return bcrypt.verify(password, user["password"])

    def add_post(self, title, tags, text):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=int(datetime.now().strftime("%s")),
            date=datetime.now().strftime("%F")
        )

        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(",")]
        tags = set(tags)

        for tag in tags:
            t = Node("Tag", name=tag)
            graph.merge(t, "Tag", "name")
            rel = Relationship(t, "TAGGED", post)
            graph.create(rel)

    def like_post(self, post_id):
        user = self.find()
        post = graph.nodes.match("Post", id=post_id).first()
        graph.merge(Relationship(user, "LIKES", post))

    def recent_posts(self, n):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = $username
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT $n
        """

        return graph.run(query, username=self.username, n=n).data()

    def similar_users(self, n):
        query = """
        MATCH (user1:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = $username AND user1<>user2
        WITH user2, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag.name) AS tag_count
        ORDER BY tag_count DESC LIMIT $n
        RETURN user2.username AS similar_user, tags
        """

        return graph.run(query, username=self.username, n=n).data()


def todays_recent_posts(n):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = $today
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT $n
    """

    today = datetime.now().strftime("%F")
    return graph.run(query, today=today, n=n).data()