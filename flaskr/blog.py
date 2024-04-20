from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
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
    if session.get('posts') is None:
        posts = db.collection('blog').get()
        posts = list(map(lambda post: post.to_dict()|{'id':post.id}, posts))
        session['posts'] = posts
    print(session['posts'])
    return render_template('blog/index.html', posts=session['posts'])



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
                        data = {'title': title, 'body': body, 'author_id': g.user['user_id'],
                                'created': time, 'author': g.user['email']}
                        db.collection('blog').document().set(data)
                        session['posts'] = session['posts'].append(data)
                except Aborted:
                    sleep(2**retry)
                finally:
                    return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    posts = session['posts']
    output_list = [dict_ for dict_ in posts if dict_.get('id') == id]
    post = output_list[0]
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
            output_list = [dict_ for dict_ in session['posts'] if dict_.get('id') == id]
            for post in output_list:
                post['title'] = title
                post['body'] = body
            post.body = body
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.collection('blog').document(post['id']).delete()
    session['posts'] = [post for post in session['posts'] if post['id'] != id]
    return redirect(url_for('blog.index'))
