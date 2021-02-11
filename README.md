# Clem

[![PyPI version](https://img.shields.io/pypi/v/clem)](https://pypi.org/project/clem/)

Simple and lightweight text variation/formatting language written in pure
Python.

## Installation
``` bash
pip install clem
```

## Usage

### Example .clem file

```
# Sections are optional, and contained within parenthesis
greeting (
    # [indicator] | [content]
    # The indicator is used to find the line in your Python program. It's referenced as 'section.indicator'.
    
    # You can add decisions by putting choices inside angle-brackets. Clem will select one at random.
    casual | How's it <hanging / going>, <bro/dude/dog/man>?
    
    # You can also nest decisions. (If a decision only contains one choice, it will be treated as an optional.)
    casual | I <<sincerely> hope / think> you will <have fun during / enjoy / <forever> remember> your stay.
    
    # You can set a choice's odds by prefixing it with '[number]:'. If ommitted this will default to 1.
    casual | <Sup / What's up>, my <2: dog / cat>? <Welcome to {location}.>
    
    # Remember you can make as many different indicators as you want.
    formal | Greetings, my <dear> <man / friend>. I <sincerely> hope you enjoy your <time/stay> here in {location}.
)
```

### Using Clem in Python

``` Python
from clem import Clem

clem = Clem()

# Load in lines
clem.load_file("example.clem")
# Add a new one at runtime
clem.add("casual | hi there! my name is <Jack <Black / White> \
         / Selena <Gomez>>.", "greeting")

# Print out line
print("Casual: ", clem.render("greeting.casual", location="Boston"))
print("Formal: ", clem.render("greeting.formal", location="Covington"))
```

## History

### Origin

Clem was originally developed for [Fallout Simulator 2]
(https://github.com/jakeledoux/fsim2) and based on the primitive templating
system of its predecessor, [Fallout Simulator]
(https://jakeledoux.itch.io/falloutsim). You can read the original format
specification [here](https://jakeledoux.github.io/fsim2/clem_docs). This version
of Clem, originally titled Clem2, was adapted from the game's code to better
structure the logic and to remove dependencies so that it could run independent
of the game.

### Name

The Clem language is named after a user by the name of 'qclem', who contributed
to the content and localisation of the templates for the original Fallout
Simulator.
