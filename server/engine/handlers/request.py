import hug

@hug.get("/request")
def request(name:str="World"):
    return "Hello, {name}".format(name=name)