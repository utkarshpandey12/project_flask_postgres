def add_cors_headers(res):
    res.headers.add("Access-Control-Allow-Origin", "*")
    res.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    res.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return res
