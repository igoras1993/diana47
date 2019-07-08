import functools
from flask import (
    Blueprint, flash, g, 
    redirect, make_response, 
    render_template, request, 
    session, url_for, current_app
)
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .primitives import BaseEvent
from . import models as gl_models
from .utils import *

blog = Blueprint('blog', __name__)

class Index(BaseEvent):
    methods = ["GET"]
    endpoint_name = "index"

    def on_get(self):
        posts = g.db_session.query(gl_models.post).all()

        return render_template('blog/index.html.j2', posts=posts)


class Create(BaseEvent):
    methods = ["GET", "POST"]
    endpoint_name = "create"

    def on_post(self):
        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            new_post = gl_models.post(author_id=g.user.id,
                                      title=title,
                                      body=body)
            
            g.db_session.add(new_post)
            g.db_session.commit()

            return redirect(url_for('blog.index'))

    def on_get(self):

        return render_template('blog/create.html.j2')


class Update(BaseEvent):
    methods = ["POST", "GET"]

    @staticmethod
    def get_post(id, check_author=True):
        try:
            db_post = g.db_session.query(gl_models.post).filter_by(id=id).one()
        except NoResultFound:
            abort(404, "Post not found.")
        
        if check_author and db_post.author.id != g.user.id:
            abord(403)

        return db_post

    def on_get(self, id):
        db_post = self.get_post(id)
        return render_template('blog/update.html.j2', post=db_post)

    def on_post(self, id):
        db_post = self.get_post(id)

        title = request.form['title']
        body = request.form['body']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db_post.title = title
            db_post.body = body
            g.db_session.commit()

            return redirect(url_for('blog.index'))


Index.register_in_blueprint(blog)
Create.register_in_blueprint(blog)
blog.add_url_rule('/<int:id>/' + Update.endpoint_name, view_func=Update.as_view(Update.endpoint_name))
