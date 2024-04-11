from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from sqlalchemy.sql.functions import current_user
from werkzeug.exceptions import abort

from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

from flaskr import firebase

from flaskr import db
from flaskr import FBauth


@login_required
@bp.route('/')
def index():
    posts = db.child('blog').get()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        time = datetime.now().isoformat()
        error = None
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            data = {'title': title, 'body': body, 'time': time, 'author_id': g.user['user_id'],
                    'created': time, 'author': g.user['email']}
            db.child('blog').push(data)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = db.child('blog').child(id).get()
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.val()['author_id'] != g.user['user_id']:
        abort(403)

    return post


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:

            db.child('blog').child(post.key()).update({'title':title,'body':body})
            post.body = body
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.child('blog').child(post.key()).delete()
    return redirect(url_for('blog.index'))
