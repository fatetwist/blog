from flask_wtf import Form
from wtforms import SubmitField, StringField,TextField,FileField
from wtforms.validators import Length, Required
from flask_pagedown.fields import PageDownField


class EditProfileForm(Form):
    avatar = FileField('头像', validators=[])
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextField('个性签名')
    submit = SubmitField('提交更改')


class PostForm(Form):
    body = PageDownField('说点什么吧', validators=[Required()])
    submit = SubmitField('发表')


class CommentForm(Form):
    body = TextField('添加评论', validators=[Required()])
    submit = SubmitField('发布')

