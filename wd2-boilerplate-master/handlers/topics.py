from handlers.base import BaseHandler
from google.appengine.api import users, memcache
from models.models import Topic, Comment
import uuid
import datetime

class TopicAdd(BaseHandler):
    def get(self):
        csrf_token = str(uuid.uuid4())
        memcache.add(key=csrf_token, value=True, time=600)
        params = {"csrf_token": csrf_token}
        return self.render_template("topic_add.html", params=params)

    def post(self):
        user = users.get_current_user()

        csrf_token = self.request.get("csrf_token")
        mem_token = memcache.get(key=csrf_token)

        if not mem_token:
            return self.write("Hacker at the doors")

        title = self.request.get("title")
        text = self.request.get("text")

        new_topic = Topic(title=title, content=text, author_email=user.email())
        new_topic.put()

        return self.redirect_to("topic-details", topic_id=new_topic.key.id())


class TopicDetails(BaseHandler):
    def get(self, topic_id):
        csrf_token = str(uuid.uuid4())
        memcache.add(key=csrf_token, value=True, time=600)

        topic = Topic.get_by_id(int(topic_id))
        comment = Comment.query(Comment.topic_id == topic.key.id()).order(Comment.created).fetch()

        params = {"topic": topic, "comment": comment, "csrf_token": csrf_token}

        return self.render_template("topic_details.html", params=params)


class CommentAdd(BaseHandler):
    def post(self, topic_id):
        user = users.get_current_user()
        time = datetime.datetime.now()

        csrf_token = self.request.get("csrf_token")
        mem_token = memcache.get(key=csrf_token)

        if mem_token:
            return self.write("Hacker at the doors")

        comment = self.request.get("comment")
        topic = Topic.get_by_id(int(topic_id))
        new_comment = Comment(content=comment, topic_id=topic.key.id(), author_email=user.email(),
                              topic_title=topic.title, created=time)
        new_comment.put()

        return self.redirect_to("topic-details", topic_id=topic.key.id())