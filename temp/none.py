from data.default.modifiers import Modifier
from data.packages.worldspawn.static.items import item
class none(item.Item):
	def __init__(self):
		super().__init__("none")

def getObject():
	return none