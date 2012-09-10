Mock Network Resources With Cork
================================

Cork is a wrapper for the [bottle.py](htttp://bottlepy.org/) micro web-framework.
Cork extends bottle.py with a launcher-type utility, as well as a Python module, `cork`,
that provides additional helper methods specific to quickly developing mock web services.

Getting Started
------------
Cork has been developed and tested on Mac OS X 10.7 using Python 2.7.3.
Other platforms and interpereter versions *should* work but have not been tested.

Cork requires the following software:
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
(particularly the section about [routing](http://bottlepy.org/docs/dev/tutorial.html#request-routing),
and the [Request](http://bottlepy.org/docs/dev/api.html#bottle.Request)
and [Response](http://bottlepy.org/docs/dev/api.html#bottle.Response) classes).

Using a Different WSGI Server
-----------------------------

Cork by default uses Bottle's built-in WSGI server based on `wsgiref`.
This server will be able to handle development and testing, and should be sufficient for light use,
but in the event that this server is insufficient
(such as when handling multiple simultaneous connections is required, or any time you experience mysterious broken pipe errors)
you will want to install/obtain a [server backend supported by Bottle](http://bottlepy.org/docs/dev/deployment.html#switching-the-server-backend).
We recommend [gevent](http://www.gevent.org/).

Use the `--server` option to set the server bottle will use (example `--server=gevent`).

Read the launcher help for the `--lib` command
if you'd prefer to simply add a downloaded server package to PYTHONPATH at runtime, instead of using a
package manager to handle user- or system- wide installation.

Examples
--------

//TODO
