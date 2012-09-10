from bottle import route, template, response
from cork import read

@route('<path:path>')
def route(path):
    log("routing '%s'" % path)
    response.content_type = "application/xml"
    response.body = template( \
                             read("data/response.xml"), \
                             to="Corky", \
                             body="Here's an example of a response from '%s'" % path \
                             )
    return(response)