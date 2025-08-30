from data.default.modifiers import Modifier
class Item:
	def __init__(self, name, max=32, modifiers=[Modifier("damage", 1), Modifier("attackCountDown", 0.5)], toolType=None, color=None):
		self.toolType = toolType
		self.modifiers = modifiers
		self.name = name
		self.max = max
		self.color = color

	def applyModifiers(self,object,hand=False):
		Modifier.applyForList(self.modifiers,object,hand)

	def getName(self):
		return self.name
		
	def getMax(self):
		return self.max
		
	def getModifiers(self):
		return self.modifiers
		
	def getColor(self):
		return self.color

	def update(self):
		pass

	def __eq__(self, other):
		return self.toolType == other.toolType and self.modifiers == other.modifiers and self.item_name == other.item_name and self.max == other.max and self.color == other.color
		

def getObject():
	return Item