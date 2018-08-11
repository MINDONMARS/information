from . import index_blue


@index_blue.route('/', methods=['GET', 'POST'])
def index():
    return 'index'
