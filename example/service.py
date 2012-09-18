from bottle import route, template, request, response
from cork import read, state, log

@route('<path:path>')
def route(path):
    log("routing '%s'" % path)
    response.content_type = "application/xml"
    
    response.body = template( \
                             read("data/response.xml"), \
                             to = state.get("to", request.headers.get("User-Agent")), \
                             body = "Here's an example of a response from '%s'" % path \
                             )
    return response