from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from google.api_core.exceptions import Aborted
from time import sleep
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)


from flaskr import db

@login_required
@bp.route('/')
def index():
    posts = db.collection('blog').get()
    posts = list(map(lambda post: post.to_dict()|{'id':post.id}, posts))
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

            for retry in range(5):
                try:
                        data = {'title': title, 'body': body, 'time': time, 'author_id': g.user['user_id'],
                                'created': time, 'author': g.user['email']}
                        db.collection('blog').document().set(data)
                except Aborted:
                    sleep(2**retry)
                finally:
                    return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = db.collection('blog').document(id).get()
    post = post.to_dict()|{'id':post.id}
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['user_id']:
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
    db.collection('blog').document(post['id']).delete()
    return redirect(url_for('blog.index'))
