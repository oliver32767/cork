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
* Python WSGI server (optional)

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
This server will be able to handle development and testing, and should be sufficient for light use.
In the event that the built-in server is insufficient
(such as when handling multiple simultaneous connections is required,
or any time you experience mysterious broken pipe errors)
you will want to install/obtain a [server backend supported by Bottle](http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend).
We recommend [gevent](http://www.gevent.org/).

Use the `--server` option to set the server bottle will use (example `--server=gevent`).

Read the launcher help for the `--lib` option if you do not have permission to
install server packages system-wide or simply don't want to.

Cork and Charles Proxy
----------------------------------------

Using a proxy server has two main advantages:

* You can use the proxy to decrypt/encrypt SSL traffic.

* No need to change hostnames/urls in the client code;
this means that you can mock services for clients you do not have the source code to.

[Charles Proxy](http://www.charlesproxy.com) is the recommended proxy to use with Cork.
It supports SSL decryption/encryption, mapping remote urls, and request/response inspection (useful for gathering canned data).
Consult the Charles Proxy documentation to configure Charles to work with your client.
Android testers should check out this
[blog post](http://jaanus.com/post/17476995356/debugging-http-on-an-android-phone-or-tablet-with)
for instructions on how to set up Android 4.0+ devices to proxy through Charles.

Listening on Multiple Ports
---------------------------
Bottle does not support listening on multiple ports, but you have a few options:

* Start multiple cork services each listening on a different port

* Use a proxy to route everything to the same port (recommended)

As an example of the second method, consider the following API endpoints:
```
http://api.example.com:7085/account
http://www.example.com:8888/search
```

In your proxy, you could map the URLs like so:
```
http://api.example.com:4040/* -> http://localhost:7085/4040/
http://www.example.com:8888/* -> http://localhost:7085/8888/
```

Now for example, the request:
    http://www.example.com:8888/search?q=search%20terms
    
maps to:
    http://localhost/8888/search?q=search%20terms


Now just define the routes:
```python
@route("/4040/<path:path>)
def handlerA(path):
    # handler code for services originally running on port 4040

@route("/8888/<path:path>)
def handlerB(path):
    # handler code for services originally running on port 8888
```

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

@route('/template/<path:path>')
def handler(path):
    tmpl = "Your request to <b>{{var}}</b> has been handled." 
    return template(tmpl, var = path)
```

Detect a specific query variable in a request and send back JSON with the correct MIME-type.
```python
from bottle import route, request, response

@route('/query')
def handler():
    query_id = request.query.id # this contains the value '12345' given the url '/query?id=12345'
    
    response.content_type = "application/json"
    response.body = '{"id":"%s"}' % query_id
    
    return response
```

Logging a message. Note: logging messages are only displayed when the `-v` option is used.
```python
from bottle import route
from cork import log

@route('/log/<path:path>')
def handler(path)
    log(path, tag = "example") # the tag argument does not need to be explicitly named, and is optional (default = "cork")
    return("<b>Your request has been logged.</b>")
```

Responding with an HTTP error.
``python
from bottle import route, HTTPError

route('/errors/<path:path>')
def handler(path):
    raise HTTPError(404, "The page you requested can not be found")
```

For more information on using Bottle, check the [Bottle API reference](http://bottlepy.org/docs/dev/api.html).