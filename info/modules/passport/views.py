from flask import request
from . import passport_blue


@passport_blue.route('/passport')
def passport(imageCode):
    pass