def exit():
    import sys
    sys.exit()


def foo(n):
    print(f'foo {n+1}')


def timer_start(*args):
    args = args[0]
    import time
    args['processor'].context['temp']['time_start'] = time.time()


def timer_end(*args):
    args = args[0]
    import time
    print("--- total duration: %s seconds ---" % (time.time() - args['processor'].context['temp']['time_start']))


def display_context(name='', *args):
    print(f'display_context({name}, {args})')
    if type(name) != str:
        args = name
        name = ''
    else:
        args = args[0]
    display(args['processor'].context, name)


def display(_dict, name=''):
    import json
    if len(name) > 0:
        print(name)
    print(json.dumps(_dict, indent=4) + '\n')


def set_var(name, value, identifier='', *args):
    if type(identifier) != str:
        args = identifier
        identifier = ''
    else:
        args = args[0]
    print(f'set_var({name}, {value}, {identifier}, {args})')
    processor = args['processor']
    if len(identifier) > 0:
        processor.context['temp'][identifier+'_'+name] = value
    else:
        processor.context['temp'][name] = value


def set_position_var(name, value, *args):
    args = args[0]
    print(f'set_position_var({name}, {value}, {args})')
    processor = args['processor']
    processor.context['data']['portfolios'][args['portfolio_index']]['positions'][args['position_index']][name] = value


def append_var(name, value, *args):
    args = args[0]
    print(f'append_var({name}, {value}, {args})')
    processor = args['processor']

    if name not in processor.context['temp']:
        processor.context['temp'][name] = []
    else:
        processor.context['temp'][name].append(value)


def is_last_position(*args):
    args = args[0]
    print(f"is_last_position {args['position_index']} {len(args['processor'].context['data']['portfolios'][args['portfolio_index']]['positions'])}")
    return args['position_index'] == len(args['processor'].context['data']['portfolios'][args['portfolio_index']]['positions'])-1


def remove_attrs(_dict, attrs):
    for attr in attrs:
        if attr in _dict:
            _dict.pop(attr)
    return _dict


functions = [
    exit,
    foo,
    display,
    display_context,
    set_var,
    set_position_var,
    append_var,
    timer_start,
    timer_end,
    is_last_position,
    sum
]
