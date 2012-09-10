Mock Web Services With Cork
================================

Cork is a wrapper for the [bottle.py](htttp://bottlepy.org/) micro web-framework.
Cork extends bottle.py with a launcher-type utility, as well as a Python module, `cork`,
that provides additional helper methods specific to quickly developing mock web services.

Getting Started
------------
Cork has been developed and tested on Mac OS X 10.7 using Python 2.7.3.
Other platforms and interpereter versions *should* work but have not been tested.

Cork has the following dependencies:
* Python 2.7+ (your system's default Python interpereter should be fine)
* bottle.py 0.10 (included in this repo)
* \[optional\] Python WSGI server (such as cherrypy or gevent)

To get started, all you need to do is clone the repository and start the example service:

    git clone git@github.com:oliver32767/cork
    chmod +x cork.py
    ./cork.py example/service.py

Now open up your web browser, and navigate to [http://localhost:7085/test](http://localhost:7085/test).
You should see some test data formatted as xml displayed in your browser window.
That's all it takes!
Press `ctrl + c` to stop the server. Run `./cork.py -h` for more information about cork's command line options.

From here you should open `example/service.py` in your editor to see how simple it can be to mock a service with cork/bottle.
See the **Examples** section for more examples of common tasks.
For more information about how to use Bottle, consult the [Bottle documentation](http://bottlepy.org/docs/dev/index.html)
(particularly the tutorial sections about [routing](http://bottlepy.org/docs/dev/tutorial.html#request-routing),
[generating content](http://bottlepy.org/docs/dev/tutorial.html#generating-content)
and [templates](http://bottlepy.org/docs/dev/tutorial.html#templates))

Using a Different WSGI Server
-----------------------------

Cork by default uses Bottle's built-in WSGI server based on `wsgiref`.
This server will be able to handle development and testing, and should be sufficient for light use,
but in the event that this server is insufficient
(such as when handling multiple simultaneous connections is required, or any time you experience mysterious broken pipe errors)
you will want to install/obtain a [server backend supported by Bottle](http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend).
We recommend [gevent](http://www.gevent.org/).

Use the `--server` option to set the server bottle will use (example `--server=gevent`).

Read the launcher help for the `--lib` option if you do not have permission to install packages system-wide or simply don't want to.

Cork, SSL, and Charles Proxy
----------------------------------------

    # TODO

Examples
--------
Define a static GET and POST route that returns the contents of a file as a response.
Note, the path given to `read()` is assumed to be relative the \*.py file passed to `cork` at execution.
```python
from bottle import route
from cork import read

@route('/static/path', method = ['GET', 'POST'])
def handler():
    return read("data/response.xml")
```

Define a dynamic route that returns a reponse generated with bottle's template engine.
```python
from bottle import route, template
from cork import read

@route('/dynamic/<path:path>')
def handler(path):
    return template(read("data/response.xml"), to="Corky", body="Here's an example of a response from '%s'" % path)
```

Detect a specific query variable in a request and send back JSON with the correct MIME-type.
```python
from bottle import request, response

@route('/query')
def handler():
    query_id = request.query.id # this contains the value '12345' given the url '/query?id=12345'
    
    response.content_type = "application/json"
    response.body = '{"id":"%s"}' % query_id
    
    return response
'''

Logging a message. Note: logging messages are only displayed when the `-v` option is used.
```python
from cork import log

@route('/example/<path:path>')
def handler(path)
    log(path)
    return("<b>your request has been logged</b>")
'''