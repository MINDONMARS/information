from flask import render_template

from . import index_blue


@index_blue.route('/', methods=['GET', 'POST'])
def index():
    return render_template('news/index.html')
