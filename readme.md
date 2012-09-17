Cork
================================

Cork is a wrapper for the [bottle.py](htttp://bottlepy.org/) micro web-framework,
and is designed to enable quick and easy creation of mock services to use while testing client applications.
Cork extends bottle.py with a launcher-type utility, and provides a Python module, `cork`,
which provides additional helper methods specific to describing mock web services.

Getting Started
------------
Cork has been developed and tested on Mac OS X 10.7 using Python 2.7.3.
Other platforms and interpereter versions *should* work but have not been tested.

Cork has the following dependencies:
* Python 2.7+ (your system's default Python interpereter should be fine)
* bottle.py 0.10 (included in this repo)
* Python WSGI server (optional)

To get started, all you need to do is clone the repository and start the example service:

    $ git clone git@github.com:RobotMonkey/cork
    $ cd cork
    $ chmod +x cork.py
    $ ./cork.py example/service.py

Now open up your web browser, and navigate to [http://localhost:7085/test](http://localhost:7085/test).
You should see some xml displayed in your browser window.
That's all it takes!
Press `ctrl + c` to stop the server. Run `./cork.py -h` for more information about cork's command line options.

### Describing a Service

From here you should open `example/service.py` in your editor to see what a basic service looks like when described with cork/bottle.
See the [Examples](#examples) section for more examples of common tasks.
For more information about how to use Bottle, consult the [Bottle tutorial](http://bottlepy.org/docs/dev/tutorial.html)
(particularly the tutorial sections about [routing](http://bottlepy.org/docs/dev/tutorial.html#request-routing),
[generating content](http://bottlepy.org/docs/dev/tutorial.html#generating-content)
and [templates](http://bottlepy.org/docs/dev/tutorial.html#templates))

Cork + Charles Proxy
----------------------------------------

Using a proxy server has two main advantages:

* You can use the proxy to decrypt/encrypt SSL traffic.
* Being able to map remote urls means that you can mock services for clients you do not have the source code to, or clients you don't want to modify.

[Charles Proxy](http://www.charlesproxy.com) is the recommended proxy to use with Cork.
It supports SSL decryption/encryption, mapping remote urls, and request/response inspection (useful for gathering canned data).
Consult the Charles Proxy documentation to configure Charles to work with your client.
Android testers should check out this
[blog post](http://jaanus.com/post/17476995356/debugging-http-on-an-android-phone-or-tablet-with)
for instructions on how to set up Android 4.0+ devices to proxy through Charles.

### Charles Proxy Links

* [Inspecting Requests & Responses](http://www.charlesproxy.com/documentation/using-charles/requests-responses/)
* [SSL Proxying](http://www.charlesproxy.com/documentation/proxying/ssl-proxying/)
* [Mapping Remote URLs](http://www.charlesproxy.com/documentation/tools/map-remote/)

Switching the Server Backend
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

Listening on Multiple Ports
---------------------------
Bottle does not support listening on multiple ports, but you have options:

* Start multiple cork services, each listening on a different port

* Use a proxy to route everything to the same port (recommended)

As an example of the second method, consider the following API endpoints:
```
http://api.example.com:4040/account
http://www.example.com:8888/search
```

In your proxy, you could map the URLs like so:
```
http://api.example.com:4040/* -> http://localhost:7085/4040/*
http://www.example.com:8888/* -> http://localhost:7085/8888/*
```

In this example, the request `http://www.example.com:8888/search?q=search%20terms` now maps to `http://localhost:7085/8888/search?q=search%20terms`.


Here's what the routes look like for this example:
```python
@route("/4040/<path:path>")
def handlerA(path):
    # handler code for services originally running on port 4040

@route("/8888/<path:path>")
def handlerB(path):
    # handler code for services originally running on port 8888
```

Setting and Getting State
----------------------------
State data is managed through a simple HTTP api available at `<host>:<port>/~cork`.
This state data is organized in a key/value pair dictionary,
accessible from within your service code by importing the Python dictionary `cork.state`.
This enables you to configure your service on the fly and can also be used to coordinate the state of your service with an external process
(useful for automated tests which may need to verify request content, for example).

### How It Works

On any given cork service, there is a special route used to perform these operations: `/~cork`.
State can be set by sending a POST request to `/~cork/<key>`; the body of this POST is the associated \<value\>.

To stop the service, make a POST to `/~cork/stop` and to reset all state data, make a POST to `/~cork/reset`; for these methods, the request's body is ignored.

To get state from a running service, send a GET request to `/~cork/<key>`.
The response will be in the form `key=value`.
If no key is specified, Cork will return all available values.

### Using cork.py to Set and Get State From a Running Cork Service

Cork comes with simple built-in utilities for setting and getting data this way.
Assume for example that we've already started a service on the default host:port;
to set state data use the command:

    $ ./cork.py --set-state "foo=bar"
    
You can also set multiple vales:
    
    $ ./cork.py --set-state "foo=bar" "baz=spaces only work if the argument is quoted"
    
After that, you can retrieve state like this:

    $ ./cork.py --get-state foo
    foo=bar

If you don't specify a key, then all values will be returned:

    $ ./cork.py --get-state
    foo=bar
    baz=spaces only work if the argument is quoted

If you request a key that doesn't exist, you get an empty string:
    
    $ ./cork.py --get-state spam
    spam=

To specify the host and/or port that the this request gets sent to, use the `--host` and/or `--port` options just as you would when starting a service.

To stop the service or reset its state, use the following commands:

    $ ./cork.py --set-state stop=true
    $ ./cork.py --set-state reset=true

----

To see this in action, start up the example service.

    $ ./cork.py example/service.py
    
Then, navigate to [http://localhost:7085/test](http://localhost:7085/test) and make a note of the `<xs:element name="to" type="xs:string">` element's value.

Issue the command:

    $ ./cork.py --set-state to=$USER
    
Reload the page in your browser and look for the new value in the `<xs:element name="to" type="xs:string">` element's value.

The `Pseudorandom` Class
------------------------
`Pseudorandom` is a custom subclass of `Random` with added facilities for generating test data (User names, email addresses, street names, etc.).
Knowing that the key to reliable testing is a controlled environment, `Pseudorandom` is designed to be given a seed value at instantiation, which can subsequently be retrieved with `.get_seed()`.
On subsequent test runs, using the same seed will result in the various functions returning the same random sequence. \\
It's important to note that maintaining a globally-scoped instance of `Pseudorandom` is probably a Bad Idea;
instead you should keep the scope of your `Pseudorandom` instances as narrow as possible. Pseudorandom also has the ability to accept an arbitrary number of seeds,
which are hashed and processed in to a single seed that the superclass uses.

## `Pseudorandom` Example

```python
from bottle import route
from cork import Pseudorandom, state

@route('/user/<username>')
def get_user_details(username):
    # storing a global seed in the state dictionary is useful, because you can adjust this setting at runtime via the /~cork api.
    
    # forst we construct a unique seed based on the global seed (in this case an Integer) and the specified username.
    # it's important to take the username in to consideration because otherwise the seed would always be the same;
    # as a consequence, each generated user would be the same.
    
    prnd = Pseudorandom(username, state.seed) # the default constructor will generate a seed based on an arbitrary number of arguments.
    
    # Pseudorandom.random_line() reads a random line from the specified text file
    full_name = prnd.random_line("/fake_data/first_names.txt") + ' ' +
                prnd.random_line("fake_data/last_names.txt") 
    
    # random_string() returns a randomly generated string based on the supplied pattern
    # The charachter '#' is replaced by a random digit 0-9, '$' yields a random uppercase letter A-Z, and '*' is replaced by a random letter OR digit)
    phone_number = prnd.random_string("(###)-###-####")
    
    # random_element() returns a random element from the supplied list
    account_type = prnd.random_element(["free", "premium", "enterprise"])
    
    return "User details for: %s<br/>Name: %s<br/>Phone number: %s<br/>Account type: %s" \
            % (username, full_name, phone_number, account_type)
```

Examples
--------
Define a static route that returns the contents of a file as a response.
Note, the path given to `read()` is assumed to be relative the \*.py file passed to `cork` at execution.
```python
from bottle import route
from cork import read

@route('/static/path')
def handler():
    return read("data/response.xml")
```

----

Define a dynamic route that returns a reponse generated with bottle's template engine.
```python
from bottle import route, template
from cork import read

@route('/template/<path:path>')
def handler(path):
    tmpl = "Your request to <b>{{var}}</b> has been handled." 
    return template(tmpl, var = path)
```

----

Define routes for a variety of http methods
```python
from bottle import route

@route('/method/get')
def handlerA():
    # ...
    
@route('/method/post', method = 'POST')
def handlerB():
    # ...
    
@route('/method/multi', method = ['GET', 'POST'])
def handlerC():
    # ...
```

----

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

----

Logging a message. Note: logged messages are only displayed when the `-v` option is used.
```python
from bottle import route
from cork import log

@route('/log/<path:path>')
def handler(path)
    log(path, tag = "example") # the tag argument does not need to be named, and is optional (default = "cork")
    return("<b>Your request has been logged.</b>")
```

----

Responding to a request with a 404 error
```python
from bottle import route, HTTPError

route('/errors/<path:path>')
def handler(path):
    raise HTTPError(404, "The page you requested can not be found")
```

----
For more information on using the Bottle api, check the [Bottle API reference](http://bottlepy.org/docs/dev/api.html).