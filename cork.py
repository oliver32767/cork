#!/usr/bin/env python
# -*- coding: utf-8 -*-

# cork
# a simple framework to rapidly mock-up network services based on templates and canned data
#
# author: Oliver Bartley
# date: 31 Aug 2012

import os, argparse, sys, types, httplib, signal
from bottle import route, request, response, run, debug, HTTPError, MultiDict

################################################################################
# Module Definition
################################################################################
# define the virtual module "cork"'s helper functions and classes
def read(filename):
    '''
    Return a string containing the contents of
    a file relative to the calling function's file path
    '''
    filename = os.path.abspath(filename)
    log("reading '%s':" % filename)
    if os.path.exists(filename):
        # open it, read it as a string and return the string
        file = open(filename, 'r')
        file_string = file.read()
        file.close()
        if debug():
            log(file_string)
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
            
def stop():
    # kill the current cork process
    print("Stopping...")
    os.kill(os.getpid(), signal.SIGKILL)
    
@route('/~cork')
def _set_state():
    # simple api for passing in state date from external processes encoded as a url query
    log("received state data:")
    
    if request.query.stop.lower() == "true":
        stop()
    
    for k in request.query.keys():
        log("%s: %s" % (k, request.query.get(k)))
        state.append(k, request.query.get(k))
        
    raise HTTPError(200)
    
state = MultiDict()

################################################################################
# Startup code
################################################################################

if __name__ == '__main__':
    # we'll create a virtual module and add it to the main namespace
    cork = types.ModuleType('cork')
    cork.state = state
    cork.read = read
    cork.log = log
    cork.stop = stop
    
    # now we just monkey-patch it in
    sys.modules['cork'] = cork

    parser = argparse.ArgumentParser(description='Run a simple mock service based on handlers in a directory tree')
    parser.add_argument("service", metavar = "SERVICE", nargs = '?', default = ".", help = "Path to the .py that describes the service")
    
    parser.add_argument("--verbose", "-v", action = 'store_true', help = "Show messages from cork.log()")
    parser.add_argument("--debug", "-d", action = 'store_true', help = "Set bottle.debug = True")
    
    #parser.add_argument("--config", metavar = "CONFIG.PY", help = "Path to a .py file to get loaded at startup. Use this to add sonfiguration options to a service.")
    parser.add_argument("--lib", metavar = "LIB", help = "Path to a directory you want added to the PYTHONPATH and thus available to your service. Useful if you do not have permission to install packages system-wide or simply don't want to.")
    parser.add_argument("--host", default = "localhost", help = "Server address to bind to. Pass 0.0.0.0 to listens on all interfaces including the external one. (default: localhost)")
    parser.add_argument("--port", default = 7085, type = int, help = "Set the port that cork listens on (default: 7085)")
    parser.add_argument("--server", default="wsgiref", help = "Switch the server backend (default: bottle.py embedded)")
    
    parser.add_argument("--reloader", action = 'store_true', help = "Enable the bottle.py reloader, useful for development purposes")
    
    parser.add_argument("--state", metavar = "STATE", help = "Helpful feature that sends an HTTP GET request in the form of: '<host>:<port>/~cork?<STATE>' This MUST be url encoded!")
    
    args = parser.parse_args()
    
    # if we've been given a STATE command, just send it and exit
    if args.state is not None:
        try:
            c = httplib.HTTPConnection(args.host, args.port)
            c.request('GET', "/~cork?%s" % args.state)
            r = c.getresponse()
            if r.status == 200:
                log("GET %s:%s?%s %d" %(args.host, args.port, args.state, r.status))
            else:
                print("GET %s:%s?%s %d (%s)" %(args.host, args.port, args.state, r.status, r.reason))
            c.close()
        except httplib.BadStatusLine:
            pass # TODO: make error handling less alarming
        exit()
        
    # otherwise, set up the environment and run the bottle server

    if args.lib is not None:
        print("adding '%s' to sys.path" % os.path.abspath(args.lib))
        sys.path.append(os.path.abspath(args.lib))
#        
#    if args.config is not None:
#        print("loading config file '%s'" % args.config)
#        config_path = os.path.abspath(args.config)
#        imp.load_source("cork.config", config_path)
    
    # set bottle's debug property
    debug(args.debug)
    log("bottle.debug = %r" % args.debug)
    
    # load the service
    
    args.service = os.path.abspath(args.service)
    os.chdir(os.path.dirname(args.service)) # switch to the directory containing the service script
    execfile(args.service)
    
    # add functionality for the gevent asynchronous wsgi server (recommended)
    if "gevent" in args.server:
        from gevent import monkey
        monkey.patch_all()

    # now start the server
    try:
        run(server = args.server, \
            host = args.host, \
            port = args.port, \
            reloader = args.reloader)
        
    except SystemExit:
        log("caught SystemExit signal, terminating")