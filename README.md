# clem2

Simple text variation and formatting language written in Python.

## Example .clem file
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

## Using Clem in Python
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
