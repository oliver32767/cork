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

# set up state handlers
state = MultiDict()
@route('/~cork')
@route('/~cork/<path:path>', method = ['GET', 'POST'])
def _state(path = ''):
    # simple api for sending/retreiving form data
    global state
    if request.method == 'POST':
        if path == '':
            log('no uri specified, using default', tag = "warning")
            path = 'default'
        elif path == "stop":
            stop()
        elif path == 'reset':
            log('resetting  state')
            state = MultiDict()
            raise HTTPError(200, "state reset")
            
        body = request.body.read()
        log("recieved new state data: %s=%s" % (path, body))
        state.append(path, body)
        return HTTPError(200, "%s=%s" % (path, body))
        
    elif request.method == 'GET':
        body = ''
        if path == '':
            for k in state.keys():
                body += "%s=%s\n" % (k, state.get(k, default = ''))
            response.body = body[:-1] # trim the last newline
        else:
            response.body = "%s=%s" % (path, state.get(path, default = ''))
        log("queried state:\n%s" % response.body)

        response.content_type = "text/plain"
        return response

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

    parser = argparse.ArgumentParser(description='Mock APIs with Bottle.py')
    parser.add_argument("service", metavar = "SERVICE", nargs = '?', default = ".", help = "Path to the .py that describes the service")
    
    parser.add_argument("--verbose", "-v", action = 'store_true', help = "Show messages from cork.log()")
    parser.add_argument("--debug", "-d", action = 'store_true', help = "Set bottle.debug = True")
    
    #parser.add_argument("--config", metavar = "CONFIG.PY", help = "Path to a .py file to get loaded at startup. Use this to add sonfiguration options to a service.")
    parser.add_argument("--lib", metavar = "LIB", help = "Path to a directory you want added to the PYTHONPATH and thus available to your service. Useful if you do not have permission to install packages system-wide or simply don't want to.")
    parser.add_argument("--host", default = "localhost", help = "Server address to bind to. Pass 0.0.0.0 to listens on all interfaces including the external one. (default: localhost)")
    parser.add_argument("--port", default = 7085, type = int, help = "Set the port that cork listens on (default: 7085)")
    parser.add_argument("--server", default="wsgiref", help = "Switch the server backend (default: bottle.py embedded)")
    
    #parser.add_argument("--reloader", action = 'store_true', help = "Enable the bottle.py reloader, useful for development purposes")
    
    parser.add_argument("--set-state", nargs = '+', metavar = "KEY=VALUE")
    parser.add_argument("--get-state", nargs = "*", metavar = "KEY")
    
    args = parser.parse_args()
    
    # if we've been given a STATE command, just send it and exit
    #if args.state is not None:
    #    try:
    #        c = httplib.HTTPConnection(args.host, args.port)
    #        c.request('GET', "/~cork?%s" % args.state)
    #        r = c.getresponse()
    #        if r.status == 200:
    #            log("GET %s:%s?%s %d" %(args.host, args.port, args.state, r.status))
    #        else:
    #            print("GET %s:%s?%s %d (%s)" %(args.host, args.port, args.state, r.status, r.reason))
    #        c.close()
    #    except httplib.BadStatusLine:
    #        pass # TODO: make error handling less alarming
    #    exit()


    # do this when the user is requesting state
    if args.get_state is not None:
        c = httplib.HTTPConnection(args.host, args.port)
        if args.get_state == []:
            c.request('GET', "/~cork")
            r = c.getresponse()
            if r.status == 200:
                print(r.read())
            c.close()
            exit()
        else:
            for q in args.get_state:
                c.request('GET', "/~cork/%s" % q)
                r = c.getresponse()
                if r.status == 200:
                    print(r.read()[:-1])
                else:
                    print(q + "=")
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
                
            try:
                c.request('POST', "/~cork/%s" % k, body = v)
                r = c.getresponse()
                if r.status != 200:
                    print("error POSTing %s=%s" % (k, v))
            except httplib.BadStatusLine:
                pass # This error happens when we send a 'stop' command
        c.close()
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