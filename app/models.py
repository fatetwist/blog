# coding=utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    comments = db.relationship('Comment', backref=db.backref('post', lazy='joined'), lazy='dynamic')

    def add_comment(self, body, user):
        if User.query.filter_by(username=user.username).first() is not None:
            c = Comment(body=body, user=user, post=self)
            db.session.add(c)


    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)), timestamp=forgery_py.date.date(True), author=u)
            db.session.add(p)
            db.session.commit()


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 用户额外信息：真实姓名、位置、个人签名、注册时间、最后登录时间
    name = db.Column(db.String(64))
    location = db.Column(db.Text())
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(128), default='\\static\\avatar\\default.png')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic')
    follower = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic')
    comments = db.relationship('Comment', backref=db.backref('user', lazy='joined'),
                               lazy='dynamic')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get('FLASKY_ADMIN'):
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        #  ?为什么不用提交
    #  定义权限检查

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMINISTER)


    #  获取所关注的人的文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    #  定义密码的处理
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    #  验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        return True

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True, name=forgery_py.name.full_name(), location=forgery_py.address.city(),
                     about_me=forgery_py.address.city(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()  # 回滚

    def follow(self, user):
        f = Follow(follower=self, followed=user)
        db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            return True
        else:
            return False

    def is_followed(self, user):
        f = self.follower.filter_by(follower_id=user.id).first()
        if f:
            return True
        else:
            return False

    # 关注、取消关注、是否关注谁、是否被谁关注


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            print(r)
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False


    def is_admin(self):
        return False


class Log_schcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    schcard_id = db.Column(db.String(64))


login_manager.anonymous_user = AnonymousUser

