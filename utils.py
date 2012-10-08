import json

def ascii_encode(x):
    try:
        return x.encode('ascii')
    except:
        return x

def ascii_code_dict(data):
    return dict(map(ascii_encode, pair) for pair in data.items())


