def get_key():
    try:
        with open('key.txt') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception('Make sure you get a key from TBA and put it in key.txt!')
        