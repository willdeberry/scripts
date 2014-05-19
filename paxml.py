#!/usr/bin/python

import re
import sys
from xml.etree.ElementTree import Element, ElementTree


def next():
    line = sys.stdin.readline()
    if line:
        line = line.rstrip( '\n' )
        line = re.sub( r'^>>> ', '', line )
    return line


root = Element( "pulse" )
context = [ root ]
this_node = context[-1]


def push_context( node ):
    context[-1].append( node )
    context.append( node )

def unwind_to_root():
    global root
    while context[-1] != root:
        context.pop()

def unwind_to_element():
    element_types = [ "module", "sink", "source", "client", "card", "sink-input", "source-output" ]
    while context[-1].tag not in element_types:
        context.pop()

def unwind_to_element_list():
    element_list_types = [ "modules", "sinks", "sources", "clients", "cards", "sink-inputs", "source-outputs" ]
    while context[-1].tag not in element_list_types:
        context.pop()


# X foo(s) available.
def on_element_list( match ):
    unwind_to_root()
    elements = re.sub( ' ', '-', match.group( 2 ) )
    # most foos that pacmd outputs are singular...
    # except one that accidentally says "1 source outputs(s) available."
    if not elements.endswith( 's' ):
        elements = elements + 's'
    push_context( Element( elements ) )


#     index: X
def on_element( match ):
    unwind_to_element_list()
    push_context( Element( re.sub( r's$', '', context[-1].tag ) ) )
    
    context[-1].set( "index", match.group( 2 ) )
    
    if match.group( 1 ) == "*":
        context[-1].set( "default", "true" )


#         name: <foo>
def on_name( match ):
    unwind_to_element()
    context[-1].set( "name", match.group( 1 ) )


#         volume: 0: X% 1: Y% ....
def on_volume( match, num_channels ):
    unwind_to_element()
    push_context( Element( "volume" ) )
    
    channels = Element( "channels" )

    index = 0
    counter = 0
    while ( counter < num_channels / 2 ):
        channel = Element( "channel" )
        channel.set( "index", str( counter ))
        channel.set( "raw_vol", str( match.group( index + 1 )))
        channel.text = match.group( index + 2 )
        index = index + 2
        counter = counter + 1
        channels.append( channel )
    
    context[-1].append( channels )
    
    context.pop()

# stereo, 2-channel volume lines
def on_stereo_volume( match ):
    on_volume( match, 4 )

# surround 5.1, 6-channel volume lines
def on_surround_volume_5_1( match ):
    on_volume( match, 12 )


#         muted: foo
def on_muted( match ):
    unwind_to_element()
    volume = context[-1].find( "volume" )
    if volume is not None:
        volume.set( "muted", match.group( 1 ) )


#          volume steps: 1234
def on_volume_steps( match ):
    unwind_to_element()
    volume = context[-1].find( "volume" )
    if volume is not None:
        volume.set( "steps", match.group( 1 ) )



#         current latency: 12.34 ms
def on_current_latency( match ):
    unwind_to_element()
    context[-1].set( "current_latency", match.group( 1 ) )


#         properties:
def on_properties( match ):
    unwind_to_element()
    push_context( Element( "properties" ) )

def on_profiles( match ):
	unwind_to_element()
	push_context( Element( "profiles" ) )


#                 foo = "bar"
# (hopefully, indented within "properties")
def on_property( match ):
    push_context( Element( match.group( 1 ) ) )
    context[-1].text = match.group( 2 )
    context.pop()


def on_profile( match ):
	push_context( Element( "profile" ) )
	context[-1].text = match.group( 1 )
	context.pop()


def on_active_profile( match ):
	unwind_to_element()
	push_context( Element( "active_profile" ) )
	context[-1].text = match.group( 1 )
	context.pop()


#         argument: <foo ...>
def on_argument( match ):
    unwind_to_element()
    argument = Element( "argument" )
    argument.text = match.group( 1 )
    context[-1].append( argument )

#         state:
def on_state( match ):
    context[-1].set( "state", match.group( 1 ) )

#         sink:
def on_sink( match ):
    context[-1].set( "sink_index", match.group( 1 ) )
    context[-1].set( "sink", match.group( 2 ) )

#         source:
def on_source( match ):
    context[-1].set( "source_index", match.group( 1 ) )
    context[-1].set( "source", match.group( 2 ) )

pattern_handlers = {
    re.compile( '^(\d+) (module|sink|source|client|card|sink input|source output)\(s\) (?:loaded|available|logged in).$' ): on_element_list,
    re.compile( '^\s+(\*| ) index: (\d+)$' ): on_element,
    re.compile( '^\s+name: <(.+)>$' ): on_name,
    re.compile( '^\s+state: (.+)$' ): on_state,
    re.compile( '^\s+sink: (\d+) <(.+)>$' ): on_sink,
    re.compile( '^\s+source: (\d+) <(.+)>$' ): on_source,
    re.compile( '^\s+volume:\s+front-left:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+front-right:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB$' ): on_stereo_volume,
    re.compile( '^\s+volume:\s+front-left:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+front-right:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+rear-left:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+rear-right:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+front-center:\s+(\d+)\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB,\s+lfe:\s+(\d)+\s+/\s+(\d+)%\s+/\s+-?\w+\.?\w+\s+dB$' ): on_surround_volume_5_1,
    re.compile( '^\s+muted: (.+)$' ): on_muted,
    re.compile( '^\s+current latency: ([0-9\.]+) ms$' ): on_current_latency,
    re.compile( '^\s+properties:$' ): on_properties,
    re.compile( '^\s+(\w[\w\.]*) = "(.*)"$' ): on_property,
    re.compile( '^\s+volume steps:\s+(\d+)$' ): on_volume_steps,
    re.compile( '^\s+argument: <(.+)>$' ): on_argument,
	re.compile( '^\s+profiles:$' ): on_profiles,
	re.compile( '^\s+((output|input|off).*):\s+(.*)$' ): on_profile,
	re.compile( '^\s+active profile:\s+<(.*)>$' ): on_active_profile,
}


current_line = next()

while current_line:
    for regex, callback in pattern_handlers.items():
        match = regex.match( current_line )
        if match:
            callback( match )
            break
    current_line = next()



print "<?xml version='1.0' standalone='yes'?>"
ElementTree( root ).write( sys.stdout )
print

