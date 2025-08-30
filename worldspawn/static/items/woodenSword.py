from data.default.modifiers import Modifier
from data.packages.worldspawn.static.items import item
class WoodenSword(item.Item):
	def __init__(self):
		super().__init__("woodenSword",32)

def getObject():
	return WoodenSword