from passlib.apps import custom_app_context as pwd_context

from gosocialserver.auth import AuthExceptions
from gosocialserver.config import DEFAULT_PROFILE_PIC
from gosocialserver.orm import Model, Select, column, Query


class User(Model):
    table_name = "users"

    def __init__(self, data=tuple()):
        super().__init__()
        self.data = data

    @property
    def username(self):
        return self._get_property(1)

    @username.setter
    def username(self, value):
        self.saved_data[1] = value

    @property
    def email(self):
        return self._get_property(2)

    @email.setter
    def email(self, value):
        self.saved_data[2] = value

    @property
    def password(self):
        return self._get_property(3)

    @password.setter
    def password(self, value):
        self.saved_data[3] = value

    @property
    def first_name(self):
        return self._get_property(4)

    @first_name.setter
    def first_name(self, value):
        self.saved_data[4] = value

    @property
    def last_name(self):
        return self._get_property(5)

    @last_name.setter
    def last_name(self, value):
        self.saved_data[5] = value

    @property
    def profile_pic(self):
        return self._get_property(6)

    @profile_pic.setter
    def profile_pic(self, value):
        self.saved_data[6] = value

    @property
    def bio(self):
        return self._get_property(7)

    @bio.setter
    def bio(self, value):
        self.saved_data[7] = value

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    def _get_property_dict(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "password": self.password,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "profile_pic": self.profile_pic,
                "bio": self.bio}

    def save(self):
        return self._save(self.table_name)

    def save_or_update(self):
        return self._save_or_update(self.table_name, User)

    @staticmethod
    def all():
        return Model._query_all(User.table_name, User)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(User.table_name, User, pk)

    @staticmethod
    def new_user(username, email, password, fn, ln):
        assert username
        assert email
        assert password
        assert fn
        assert ln

        user = Select().fields(["id"]).From(User.table_name) \
            .filter(column("email").equal(email)) \
            .Or() \
            .filter(column("username").equal(username)) \
            .to_query().with_model(User).first()

        if user:
            raise AuthExceptions.UserExistException()

        user = User()
        user.id = None
        user.username = username
        user.email = email
        user.password = User.generate_password_hash(password)
        user.first_name = fn
        user.last_name = ln
        user.profile_pic = DEFAULT_PROFILE_PIC

        pk = user.save()
        if not pk:
            raise AuthExceptions.FailedRegistration()

        user.id = pk
        return user

    @staticmethod
    def check_user(username, password):
        assert username
        assert password

        user = Select().star() \
            .From(User.table_name) \
            .filter(column("username").equal(username)) \
            .to_query().with_model(User) \
            .first()

        if user and User.verify_password(user.password, password):
            return user

        return None

    @staticmethod
    def generate_password_hash(password):
        return pwd_context.encrypt(password)

    @staticmethod
    def verify_password(self_password, password):
        return pwd_context.verify(password, self_password)


class Post(Model):
    table_name = "posts"

    def __init__(self, data=tuple()):
        super().__init__()
        self.data = data
        print(self.data)

    @property
    def title(self):
        return self._get_property(1)

    @title.setter
    def title(self, value):
        self.saved_data[1] = value

    @property
    def body(self):
        return self._get_property(2)

    @body.setter
    def body(self, value):
        self.saved_data[2] = value

    @property
    def image(self):
        return self._get_property(3)

    @image.setter
    def image(self, value):
        self.saved_data[3] = value

    @property
    def created_on(self):
        return self._get_property(4)

    @created_on.setter
    def created_on(self, value):
        self.saved_data[4] = value

    @property
    def updated_on(self):
        return self._get_property(5)

    @property
    def author(self):
        u = self._get_property(6)

        if not isinstance(u, User):
            self.load()
            u = self._get_property(6)

        return u

    @author.setter
    def author(self, value):
        self.saved_data[6] = value

    @property
    def author_username(self):
        return self._get_property(7)

    @property
    def author_profile_pic(self):
        return self._get_property(8)

    @property
    def like_count(self):
        return Like.get_count_for(self)

    @property
    def dislike_count(self):
        return Dislike.get_count_for(self)

    @property
    def comments(self):
        comments = self._get_property(16)
        if not comments:
            comments = Select().star().From(Comment.table_name) \
                .filter(column('post_id').equal(self.id)) \
                .to_query().with_model(Comment) \
                .all()

            self.saved_data[16] = comments

        return comments

    def _get_property_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "image": self.image,
            "created_on": self.created_on,
            "user_id": self.author.id
        }

    def delete(self):
        sql = "delete from %s where `id` = %d" % (self.table_name, self.id)
        cur = Query(sql).execute()
        cur.close()

    def save_or_update(self):
        return self._save_or_update(self.table_name, Post)

    def save(self):
        return self._save(self.table_name)

    def load(self):
        pk = self._get_property(6)
        if not type(pk) is int:
            return

        u = Select().star().From(User.table_name) \
            .filter(column("id").equal(pk)) \
            .to_query().with_model(User) \
            .first()
        if not u:
            return

        self.author = u

    @staticmethod
    def all():
        return Model._query_all(Post.table_name, Post)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Post.table_name, Post, pk)

    @staticmethod
    def new_post(title, body, image_url, user):
        assert title
        assert isinstance(user, User)

        post = Post()
        post.title = title
        post.body = body if body and len(body) > 0 else None
        post.image = image_url
        post.author = user
        post.created_on = None

        pk = post.save()
        post.id = pk

        return post

    @staticmethod
    def get_main_page_posts():
        sql = """SELECT P.id,P.title, P.body,P.image, P.created_on,P.updated_on, P.user_id, U.username,U.profile_pic
            FROM posts P, users U
            WHERE (P.user_id = U.id)
            GROUP By P.id
            ORDER BY id DESC"""

        return Query(sql).with_model(Post).all()


class Comment(Model):
    table_name = "comments"

    def __init__(self, data=tuple()):
        super().__init__()
        self.data = data

    @property
    def body(self):
        return self._get_property(1)

    @body.setter
    def body(self, value):
        self.saved_data[1] = value

    @property
    def created_on(self):
        return self._get_property(2)

    @created_on.setter
    def created_on(self, value):
        self.saved_data[2] = value

    @property
    def parent(self):
        u = self._get_property(3)

        if u and not isinstance(u, Comment):
            self.load_parent()
            u = self._get_property(3)

        return u

    @parent.setter
    def parent(self, value):
        self.saved_data[3] = value

    @property
    def parent_id(self):
        return self.data[3]

    @property
    def post(self):
        u = self._get_property(4)

        if u and not isinstance(u, Post):
            self.load_post()
            u = self._get_property(4)

        return u

    @post.setter
    def post(self, value):
        self.saved_data[4] = value

    @property
    def post_id(self):
        return self.data[4]

    @property
    def author(self):
        u = self._get_property(5)

        if not isinstance(u, User):
            self.load_user()
            u = self._get_property(5)

        return u

    @author.setter
    def author(self, value):
        self.saved_data[5] = value

    @property
    def children(self):
        children = self._get_property(6)
        if not children:
            children = self.saved_data[6] = self.get_child_comments()

        return children

    def _get_property_dict(self):
        return {
            "id": self.id,
            "body": self.body,
            "parent_id": self.parent.id if self.parent else None,
            "post_id": self.post.id if self.post else None,
            "user_id": self.author.id
        }

    def load_parent(self):
        pk = self._get_property(3)
        if not type(pk) is int:
            return

        c = Select().star().From(Comment.table_name) \
            .filter(column("id").equal(pk)) \
            .to_query().with_model(Comment) \
            .first()
        if not c:
            return

        self.parent = c

    def load_post(self):
        pk = self._get_property(4)
        if not type(pk) is int:
            return

        p = Select().star().From(Post.table_name) \
            .filter(column("id").equal(pk)) \
            .to_query().with_model(Post) \
            .first()

        if not p:
            return

        self.post = p

    def load_user(self):
        pk = self._get_property(5)
        if not type(pk) is int:
            return

        u = Select().star().From(User.table_name) \
            .filter(column("id").equal(pk)) \
            .to_query().with_model(User) \
            .first()

        if not u:
            return

        self.author = u

    def get_child_comments(self):
        assert self.id

        return [cm1 for cm1 in Select().star().From(Comment.table_name).filter(
            column("parent_id").equal(self.id)).to_query().with_model(Comment).all()]

    def save(self):
        return self._save(Comment.table_name)

    def save_or_update(self):
        return self._save_or_update(Comment.table_name, Comment)

    @staticmethod
    def all():
        return Model._query_all(Comment.table_name, Comment)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Comment.table_name, Comment, pk)

    @staticmethod
    def new_comment(body, parent, post, user):
        assert body
        assert user
        assert (parent and not post) or (post and not parent)

        comment = Comment()
        comment.body = body
        comment.parent = parent
        comment.post = post
        comment.author = user

        pk = comment.save()
        comment.id = pk

        return comment


class Like(Model):
    table_name = "likes"

    def __init__(self, data=tuple()):
        super().__init__()
        self.data = data

    @property
    def post(self):
        u = self._get_property(2)

        if not isinstance(u, User):
            self.load_post()
            u = self._get_property(2)

        return u

    @post.setter
    def post(self, value):
        self.saved_data[2] = value

    @property
    def author(self):
        u = self._get_property(3)

        if not isinstance(u, User):
            self.load_user()
            u = self._get_property(3)

        return u

    @author.setter
    def author(self, value):
        self.saved_data[3] = value

    @property
    def created_on(self):
        return self._get_property(4)

    @created_on.setter
    def created_on(self, value):
        self.saved_data[4] = value

    def _get_property_dict(self):
        return {
            "id": self.id,
            "post_id": self.post.id,
            "user_id": self.author.id,
            "created_on": self.created_on
        }

    def load_post(self):
        pk = self._get_property(2)
        if not type(pk) is int:
            return

        u = Post.get_by_id(pk)
        if not u:
            return

        self.post = u

    def load_user(self):
        pk = self._get_property(3)
        if not type(pk) is int:
            return

        u = User.get_by_id(pk)
        if not u:
            return

        self.author = u

    @staticmethod
    def all():
        return Model._query_all(Like.table_name, Like)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Like.table_name, Like, pk)

    def save(self):
        return self._save(self.table_name)

    def save_or_update(self):
        return self._save_or_update(self.table_name, Like)

    def delete(self):
        sql = "delete from %s where `id` = %d" % (self.table_name, self.id)
        print(sql)
        cur = Query(sql).execute()
        cur.close()

    @staticmethod
    def new(post, user):
        assert post
        assert user

        like = Like()
        like.post = post
        like.author = user
        like.created_on = None

        pk = like.save()
        like.id = pk

        return like

    @staticmethod
    def get_count_for(post):
        sql = "SELECT COUNT(*) as like_counts FROM %s WHERE post_id = %s" % (Like.table_name, post.id)
        counts = Query(sql).with_model(Like).first()
        return counts.id if counts else 0


class Dislike(Like):
    table_name = "dislikes"

    def __init__(self, data=tuple()):
        super().__init__()
        self.data = data

    @staticmethod
    def all():
        return Model._query_all(Dislike.table_name, Dislike)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Dislike.table_name, Dislike, pk)

    @staticmethod
    def new(post, user):
        assert post
        assert user

        like = Dislike()
        like.post = post
        like.author = user
        like.created_on = None

        pk = like.save()
        like.id = pk

        return like

    @staticmethod
    def get_count_for(post):
        sql = "SELECT COUNT(*) as dislike_counts FROM %s WHERE post_id = %s" % (Dislike.table_name, post.id)
        counts = Query(sql).with_model(Like).first()
        return counts.id if counts else 0


if __name__ == '__main__':
    # cm = Comment.get_by_id(2)
    # from jinja2 import Environment, PackageLoader
    # env = Environment(loader=PackageLoader('gosocialserver', 'templates'))
    # template = env.get_template('comment.html')
    # print(template.render(comment=cm))
    pass
    # user = User.get_by_id(6)
    # post = Post.get_by_id(5)
    #
    # # like = Like.new(post, user)
    # like = Dislike.new(post, user)
    #
    # print(like.post.id)
