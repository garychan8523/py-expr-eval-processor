import math
from ast import *
import operator


def literal_eval(node_or_string, variables={}, functions=[]):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, and None.
    """
    _functions = { function.__name__: function for function in functions }

    if isinstance(node_or_string, str):
        node_or_string = parse(node_or_string.lstrip(" \t"), mode='eval')
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    def _raise_malformed_node(node):
        msg = "malformed node or string"
        if lno := getattr(node, 'lineno', None):
            msg += f' on line {lno}'
        raise ValueError(msg + f': {node!r}')
    def _convert_num(node):
        if not isinstance(node, Constant) or type(node.value) not in (int, float, complex):
            _raise_malformed_node(node)
        return node.value
    def _convert_signed_num(node):
        if isinstance(node, UnaryOp) and isinstance(node.op, (UAdd, USub)):
            operand = _convert_num(node.operand)
            if isinstance(node.op, UAdd):
                return + operand
            else:
                return - operand
        return _convert_num(node)
    def _convert(node):
        print(f'evaluating {node}')

        def checkmath(x, *args):
            if x not in [x for x in dir(math) if not "__" in x]:
                raise SyntaxError(f"Unknown func {x}()")
            fun = getattr(math, x)
            return fun(*args)

        binOps = {
                Add: operator.add,
                Sub: operator.sub,
                Mult: operator.mul,
                Div: operator.truediv,
                Mod: operator.mod,
                Pow: operator.pow,
                Call: checkmath,
                BinOp: BinOp
            }

        unOps = {
                USub: operator.neg,
                UAdd: operator.pos,
                UnaryOp: UnaryOp
        }

        ops = tuple(binOps) + tuple(unOps)

        if isinstance(node, Constant):
            return node.value
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return list(map(_convert, node.elts))
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, Subscript):
            print('in Subscript')
            key = node.slice.value

            if node.value.id == 'context':
                return variables['processor'].context[key]
            elif node.value.id == 'temp':
                return variables['processor'].context['temp'][key]
            elif node.value.id == 'data':
                return variables['processor'].context['data'][key]
            elif node.value.id == 'portfolio':
                return variables['processor'].context['data']['portfolios'][variables['portfolio_index']][key]
            elif node.value.id == 'position':
                return variables['processor'].context['data']['portfolios'][variables['portfolio_index']]['positions'][variables['position_index']][key]
            else:
                return variables[node.value.id]
        elif (isinstance(node, Call) and isinstance(node.func, Name) and
              node.func.id == 'set' and node.args == node.keywords == []):
            return set()
        elif (isinstance(node, Call) and isinstance(node.func, Name) and node.func.id == '_if'):
            return _convert(node.args[1]) if _convert(node.args[0]) else _convert(node.args[2])
        elif (isinstance(node, Call) and isinstance(node.func, Name) and node.func.id in _functions.keys()):
            print('in Call')
            print(f'node.fun {node.func}')
            print(f'node.func.id {node.func.id}')
            print(f'node.args {node.args}')
            args = [_convert(arg) for arg in node.args]
            _t = args.copy()
            args.append(variables)
            args = tuple(args)
            print(f'args {args}')
            print(f'node.keywords {node.keywords}')
            # print(f'functions {functions}')
            try:
                return _functions[node.func.id](*args)
            except:
                args = _t
                args = tuple(args)
                return _functions[node.func.id](*args)
        elif isinstance(node, Dict):
            if len(node.keys) != len(node.values):
                _raise_malformed_node(node)
            return dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        elif isinstance(node, BinOp):
            print("BinOp")
            if isinstance(node.left, ops) or isinstance(node.left, Subscript):
                left = _convert(node.left)
            else:
                left = node.left.value
            print(f'left {left}')
            if isinstance(node.right, ops) or isinstance(node.right, Subscript):
                right = _convert(node.right)
            else:
                right = node.right.value
            print(f'right {right}')
            return binOps[type(node.op)](left, right)
        elif isinstance(node, UnaryOp):
            print("UpOp")
            if isinstance(node.operand, ops):
                operand = _convert(node.operand)
            else:
                operand = node.operand.value
            return unOps[type(node.op)](operand)
        else:
            raise SyntaxError(f"Bad syntax, {type(node)}")
    return _convert(node_or_string)

