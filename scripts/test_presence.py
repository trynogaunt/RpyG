import time
from pypresence import Presence

rpc = Presence("1439725986290860132")
rpc.connect()
rpc.update(details="Test", state="Ça marche")
print("Envoyé")
time.sleep(60)