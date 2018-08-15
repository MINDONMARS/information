
def do_rank(index):
    """
    自定义过滤器: 根据index返回first, second, third, ''
    :return:first, second, third
    """
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''