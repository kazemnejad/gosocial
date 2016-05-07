from passlib.apps import custom_app_context as pwd_context

from gosocialserver.auth import AuthExceptions
from gosocialserver.orm import Model, Select, column, Insert


class User(Model):
    table_name = "users"

    def __init__(self, data=tuple):
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
    def name(self):
        return self.first_name + " " + self.last_name

    def _get_property_dict(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "password": self.password,
                "first_name": self.first_name,
                "last_name": self.last_name}

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

        pk = Insert().into(User.table_name).values(user._get_property_dict()).to_query().execute()
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

        raise AuthExceptions.InvalidCredentialsException()

    @staticmethod
    def generate_password_hash(password):
        return pwd_context.encrypt(password)

    @staticmethod
    def verify_password(self_password, password):
        return pwd_context.verify(password, self_password)


class Post(Model):
    table_name = "posts"

    def __init__(self, data):
        super().__init__()
        self.data = data

    @staticmethod
    def all():
        return Model._query_all(Post.table_name, Post)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Post.table_name, Post, pk)


class Comment(Model):
    table_name = "comments"

    def __init__(self, data):
        super().__init__()
        self.data = data

    @staticmethod
    def all():
        return Model._query_all(Comment.table_name, Comment)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Comment.table_name, Comment, pk)


class Like(Model):
    table_name = "likes"

    def __init__(self):
        super().__init__()

    @staticmethod
    def all():
        return Model._query_all(Like.table_name, Like)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Like.table_name, Like, pk)


class Dislike(Model):
    table_name = "dislikes"

    def __init__(self, data):
        super().__init__()
        self.data = data

    @staticmethod
    def all():
        return Model._query_all(Dislike.table_name, Dislike)

    @staticmethod
    def get_by_id(pk):
        return Model._query_by_id(Dislike.table_name, Dislike, pk)


if __name__ == '__main__':
    # user = User.new_user("admin", "root@localhost", "pass", "Mr.Admin", "Admini")
    user = User.check_user("admin", "pass")
    print(user)
