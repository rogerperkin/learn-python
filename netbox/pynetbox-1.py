import pynetbox 

nb = pynetbox.api(url="http://localhost:8000", token="f8908181dcc5ede256e8610b8b374adcb43b457")

all_prefixes = nb.ipam.prefixes.all()

print(all_prefixes)