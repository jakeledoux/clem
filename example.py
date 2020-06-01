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
