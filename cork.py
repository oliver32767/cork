#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cork
# a simple framework to rapidly mock-up network services based on templates and canned data
#
# author: Oliver Bartley
# date: 31 Aug 2012

import os, argparse, sys, types, httplib, signal
from random import Random
from bottle import route, request, response, run, debug, HTTPError, MultiDict

################################################################################
# Module Definition
################################################################################
# define the virtual module "cork"'s helper functions and classes

class Pseudorandom(Random):
    '''
    Pseudorandom works by maintaining the state of a random number generator
    with a known seed. Using this seed in a different instance
    will result in the same random sequence being generated repeatedly.
    '''
    _seed = None
    
    def __new__(self, *args, **kwargs):
        '''
        for reasons unbeknownst to me, this is required to subclass Random()
        '''
        return super(Pseudorandom, self).__new__(self)

    def __init__(self, *args):
        Random.__init__(self)
        self.seed(*args)
        
    def seed(self, *args):
        '''overridden seed method, now accepts an iterable container of hashable objects'''
        self._seed = self.hash_args(*args)
        super(Pseudorandom, self).seed(self._seed)
        return self._seed
        
    def hash_args(self, *args):
        '''
        When passed a list of args, will iterate over each args and XOR it to previous hashes to generat this instance's seed value
        from a list of hashable objects. If an object is not hashable, we attempt to convert it into a string before hashing.
        Returns None if no args are given.
        '''
        if len(args) == 0:
            return None
        rv = 0
        
        for arg in args:
            unhashable = False
            
            try:
                rv = rv ^ arg.__hash__() # XOR bitwise operation
            except TypeError:
                unhashable = True
                
            if unhashable:
                # this means that the arg isn't hashable
                try:
                    rv = rv ^ str(arg).__hash__() # attemt to convert it into a string, then hash it
                except:
                    raise TypeError("Argument cannot be hashed or converted into a String")
        return rv
        
    def get_seed():
        return _seed

    
    def choice(self, *elements):
        '''
        overridden choice() implementation.
        adds support for *args
        '''
        if len(elements) == 0:
            return None
        elif len(elements) == 1:
            return elements[0][self.randrange(0, len(elements[0]))]
        else:
            return elements[self.randrange(0, len(elements))]

    def random_string(self, pattern):
        '''
        random_string takes a pattern and returns a generated string based on the pattern.
        # is replaced with a digit [0..9]
        $ is replaced with an uppercase letter [A..Z]
        * is replaced with a random digit or uppercase letter [0..9, A..Z]
        '''
        
        chars = {"#": "0123456789",
                 "$": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                 "*": "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                }

        rv = ''
        for c in pattern:
            if c in chars:
                rv += self.random_element(chars[c])
            else:
                rv += c
        return rv
    
    def random_line(self, filename):
        '''
        return a pseudorandom line from the specified file
        thanks to http://www.regexprn.com/2008/11/read-random-line-in-large-file-in.html
        '''
        file = open(filename,'r')

        #Get the total file size
        file_size = os.stat(filename)[6]
        
        while 1:
            #Seek to a place in the file which is a random distance away
            #Mod by file size so that it wraps around to the beginning
            file.seek((file.tell() + self.randint(0, file_size - 1)) % file_size)
        
            #dont use the first readline since it may fall in the middle of a line
            file.readline()
            #this will return the next (complete) line from the file
            line = file.readline().strip()
            
            if line != "":
                return line


def read(filename):
    '''
    Return a string containing the contents of
    a file relative to the calling function's file path
    '''
    filename = os.path.abspath(filename)
    debug("reading '%s':" % filename)
    if os.path.exists(filename):
        # open it, read it as a string and return the string
        file = open(filename, 'r')
        file_string = file.read()
        file.close()
        debug(file_string)
        return(file_string)
    else:
        log("file not found: %s" % filename)
        raise HTTPError(404)
    
def log(message, tag = None):
    # log a message (and tag, if provided) if --verbosity is set
    global args
    if args.verbose:
        if tag is None:
            tag = "cork"
        print("%s:%s" % (tag, message))

def debug(message, tag = None):
    # log a message if debug is set
    global args
    if args.debug:
        if tag is None:
            tag = "debug"
        log(message, tag)

def stop():
    # kill the current cork process
    print("Stopping...")
    os.kill(os.getpid(), signal.SIGKILL)

def reset():
    debug('resetting  state')
    state = {}

# set up state handlers
state = {}
@route('/~cork')
@route('/~cork/<path:path>', method = ['GET', 'POST'])
def _state_handler(path = ''):
    # simple api for sending/retreiving form data
    global state
    if request.method == 'POST':
        if path == '':
            debug('no uri specified, using default', tag = "warning")
            path = 'default'
        elif path == "stop":
            stop()
        elif path == 'reset':
            reset()
            raise HTTPError(200, "state reset")
            
        body = request.body.read()
        debug("recieved new state data: %s=%s" % (path, body))
        state[path] = body
        return HTTPError(200, "%s=%s" % (path, body))
        
    elif request.method == 'GET':
        if path == '':
            body = ''
            if len(state) == 0:
                print("derp")
                response.body = ''
            else:
                
                for k in state.keys():
                    print("herp")
                    body += "%s=%s\n" % (k, state.get(k, ''))
                response.body = body[:-1] # trim the last newline
        else:
            response.body = state.get(path, '')
        
        debug("queried state:\n'%s'" % response.body)
        
        response.content_type = "text/plain"
        return response

################################################################################
# Startup code
################################################################################

if __name__ == '__main__':
    # we'll create a virtual module and add it to the main namespace
    cork = types.ModuleType('cork')
    cork.Pseudorandom = Pseudorandom
    cork.state = state
    cork.read = read
    cork.log = log
    cork.stop = stop
    cork.reset = reset
    
    # now we just monkey-patch it in
    sys.modules['cork'] = cork

    parser = argparse.ArgumentParser(description='Mock APIs with Bottle.py')
    parser.add_argument("service", metavar = "SERVICE", nargs = '?', default = None, help = "Path to the .py that describes the service")
    
    parser.add_argument("--verbose", "-v", action = 'store_true', help = "Show messages from cork.log()")
    parser.add_argument("--debug", "-d", action = 'store_true', help = "Set bottle.debug = True")
    
    
    parser.add_argument("--lib", metavar = "LIB", help = "Path to a directory you want added to the PYTHONPATH and thus available to your service. Useful if you do not have permission to install packages system-wide or simply don't want to.")
    parser.add_argument("--host", default = "localhost", help = "Server address to bind to. Pass 0.0.0.0 to listens on all interfaces including the external one. (default: localhost)")
    parser.add_argument("--port", default = 7085, type = int, help = "Set the port that cork listens on (default: 7085)")
    parser.add_argument("--server", default="wsgiref", help = "Switch the server backend (default: wsgiref)")
    
    parser.add_argument("--config", metavar = "CONFIG.PY", help = "Path to a .py file to get loaded at startup. Use this to add configuration options to a service.")
    
    parser.add_argument("--set-state", nargs = '+', metavar = "KEY=VALUE", help = "Send a POST request to <HOST>:<PORT>/~cork/<KEY> to associate <VALUE> with <KEY> in the recieving service's state dictionary.")
    parser.add_argument("--get-state", nargs = "*", metavar = "KEY", help = "Send a GET request to <HOST>:<PORT>/~cork/<KEY> to retrieve the value associated with <KEY>. If <KEY> is not specified, returns all currently set values.")
    
    args = parser.parse_args()
    
    # do this when the user is requesting state
    if args.get_state is not None:
        c = httplib.HTTPConnection(args.host, args.port)
        if args.get_state == []:
            c.request('GET', "/~cork")
            r = c.getresponse()
            if r.status == 200:
                if len(r.read()) > 0:
                    print(r.read())
        else:
            for q in args.get_state:
                c.request('GET', "/~cork/%s" % q)
                r = c.getresponse()
                print(r.read())
        c.close()
        exit()
        
    # do this when the user is sending state
    if args.set_state is not None:
        c = httplib.HTTPConnection(args.host, args.port)
        for kv in args.set_state:
            try:
                k = kv.split('=')[0]
                v = kv.split('=')[1]
            except IndexError:
                print('Argument must be in the form "KEY=VALUE" (was "%s")' % kv)
                exit(-1)
            if args.service is None:
                # if no service is passed, we assume we're setting it via HTTP
                try:
                    c.request('POST', "/~cork/%s" % k, body = v)
                    r = c.getresponse()
                    if r.status != 200:
                        raise RuntimeError("error POSTing %s=%s (status %d)" % (k, v, r.status))
                except httplib.BadStatusLine:
                    pass # This error happens when we send a 'stop' command
            else:
                # otherwise, it means we just set the state directly, and then load the service
                cork.state[k] = v
                
        c.close()
        if args.service is None:
            exit()
        
    # otherwise, set up the environment and run the bottle server
    if args.lib is not None:
        print("adding '%s' to sys.path" % os.path.abspath(args.lib))
        sys.path.append(os.path.abspath(args.lib))

    # load the config file if we're given one
    if args.config is not None:
        print("loading config file '%s'" % args.config)
        config_path = os.path.abspath(args.config)
        imp.load_source("cork.config", config_path)
    
    if args.verbose:
        # :)
        log("cork is being verbose")
        
    # set bottle's debug property
    debug(args.debug)
    if args.debug:
        args.verbose = True
    debug("bottle.debug = %r" % args.debug)
    
    # load the service
    args.service = os.path.abspath(args.service)
    os.chdir(os.path.dirname(args.service)) # switch to the directory containing the service script
    try:
        execfile(args.service)
    except IOError:
        print("There was an error loading the service '%s'" % args.service)
        exit(-1)
        
    # add functionality for the gevent asynchronous wsgi server (recommended)
    if "gevent" in args.server:
        from gevent import monkey
        monkey.patch_all()

    # now start the server
    try:
        run(server = args.server, \
            host = args.host, \
            port = args.port)
            #reloader = args.reloader)

    except SystemExit:
        log("caught SystemExit signal, terminating")