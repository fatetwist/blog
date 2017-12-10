# coding=utf-8
from . import main
from flask import render_template, request, flash, redirect, url_for, current_app, abort, make_response
from ..models import User, Post, Permission, Follow, AnonymousUser
from .forms import EditProfileForm, PostForm, CommentForm
from flask_login import current_user, login_required
from .. import db
import os
from datetime import datetime
from ..decorators import permission_required
from ..models import Comment
from .. import getrest

@main.route('/', methods=['POST', 'GET'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    page = request.args.get('page', 1, type=int)

    if show_followed:
        query = current_user.followed_posts

    else:
        query = Post.query

    pagination = query.order_by(Post.timestamp.desc()).paginate(page,
                                                                per_page=current_app.config['FLASKY_PER_PAGE'],
                                                                error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, form=form, pagination=pagination, show_followed=show_followed)


@main.route('/all')
@login_required
def all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp



@main.route('/user')
def user():
    page = request.args.get('page', 1, type=int)
    username = request.args.get('username')
    u = User.query.filter_by(username=username).first()
    pagination = u.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['FLASKY_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user.html', user=u, posts=posts, pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    @login_required
    def send_comment():
        post.add_comment(user=user, body=body)
    form = CommentForm()
    post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        body = form.body.data
        user = current_user._get_current_object()
        send_comment()
        return redirect(url_for('.post', id=id))
    comments = post.comments.order_by(Comment.timestamp.desc()).all()
    return render_template('post.html', posts=[post], p=post, form=form, comments=comments)


@main.route('/EditProfile', methods=['POST', 'GET'])
@login_required
def EditProfile():
    u_id = request.args.get('id', -1, type=int)
    if u_id == -1:
        u = current_user._get_current_object()
    else:
        u = User.query.filter_by(id=u_id).first()
    form = EditProfileForm()
    if form.validate_on_submit():

        u.name = form.name.data
        u.location = form.location.data
        u.about_me = form.about_me.data
        avatar = request.files.get('avatar', None)
        fname = avatar.filename
        if fname != '':
            UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'avatar')
            print('头像文件上传位置：' + UPLOAD_FOLDER)
            ALLOWED_EXTENSIONS = ['png', 'gif', 'jpeg', 'jpg']
            flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
            if not flag:
                flash('文件类型错误')
                return redirect(url_for('main.user', username=u.username))
            img_name = '{}_{}'.format(u.username, fname)
            img_save = os.path.join(UPLOAD_FOLDER, img_name)
            avatar.save(img_save)
            u.avatar = '/static/avatar/{}_{}'.format(current_user.username,fname)
        db.session.add(current_user)
        flash('个人资料已经修改！')
        return redirect(url_for('main.user', username=u.username))


    form.name.data = u.name
    form.location.data = u.location
    form.about_me.data = u.about_me

    return render_template('EditProfile.html', form=form, u=u)


@main.route('/Edit-post/<int:id>', methods=['POST', 'GET'])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.timestamp = datetime.utcnow()
        db.session.add(post)
        return redirect(url_for('.index'))
    form.body.data = post.body
    return render_template('EditPost.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    u = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在！')
        return redirect(url_for('.index'))
    if current_user == u:
        flash('不能关注自己！')
        return redirect(url_for('.user', username=username))
    if current_user.followed.filter_by(followed_id=u.id).first():
        flash('您已经关注过该用户了，找其他人关注去吧')
        return redirect(url_for('.user', username=username))

    # u 成为可关注对象
    f = Follow(follower=current_user._get_current_object(), followed=u)
    db.session.add(f)
    flash('关注成功！')
    return redirect(url_for('.user', username=username))


@main.route('/schcard', methods=['POST', 'GET'])
def schcard():
    if request.method == 'GET':
        return render_template('schcard.html')
    else:
        schcard_id = request.form.get('schcard_id')
        head_url = "http://www.ccb.com/tran/WCCMainPlatV5"
        headers = getrest.getHeaders(head_url)
        resp = getrest.getRest(schcard_id, headers)
        return render_template('schcard.html', schcard_resp=resp)
