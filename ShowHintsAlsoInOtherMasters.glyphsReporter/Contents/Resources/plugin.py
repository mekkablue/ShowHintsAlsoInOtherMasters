# encoding: utf-8
from __future__ import division, print_function, unicode_literals

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSRect

class ShowHintsAlsoInOtherMasters(ReporterPlugin):
	rgbH = 0.1, 0.5, 0.8
	rgbV = 0.8, 0.5, 0.1
	alphaDark = 0.6
	alphaLight = 0.2
	
	prefID = "com.mekkablue.ShowHintsAlsoInOtherMasters"
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'PS Hints Also in Other Masters',
			'de': 'PS-Hints auch in anderen Mastern',
			'fr': 'hints PS aussi dans les autres masters',
			'es': 'hints PS también en los otros másteres',
		})
		
		Glyphs.registerDefault(self.domain("verticalStemHints"), True)
		Glyphs.registerDefault(self.domain("horizontalStemHints"), True)
		Glyphs.registerDefault(self.domain("ghostHints"), True)
	
	@objc.python_method
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	@objc.python_method
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	@objc.python_method
	def rectifyRect(self, rect):
		"""Converts rect with negative size into positive size."""
		newRectOriginX = rect.origin[0]
		newRectOriginY = rect.origin[1]
		newRectSizeWidth = rect.size[0]
		newRectSizeHeight = rect.size[1]
		
		if newRectSizeWidth < 0:
			newRectSizeWidth *= -1
			newRectOriginX -= newRectSizeWidth
		if newRectSizeHeight < 0:
			newRectSizeHeight *= -1
			newRectOriginY -= newRectSizeHeight
			
		newRect = NSRect(
			(newRectOriginX, newRectOriginY),
			(newRectSizeWidth, newRectSizeHeight)
		)
		return newRect
	
	@objc.python_method
	def background(self, layer):
		glyph = layer.parent
		if glyph:
			font = glyph.parent
			if font:
				windowController = font.parent.windowController()
				if not windowController.SpaceKey():
					self.drawHints(layer)
	
	@objc.python_method
	def preview(self, layer):
		if not Glyphs.defaults["GSPreview_Black"]:
			# white background:
			self.drawHints(
				layer, size=20, vsize=5000,
				inPreview = True,
			)
		else:
			# black background:
			self.drawHints(
				layer, size=20, vsize=5000,
				hColor = NSColor.colorWithRed_green_blue_alpha_(*(self.rgbH), self.alphaDark),
				vColor = NSColor.colorWithRed_green_blue_alpha_(*(self.rgbV), self.alphaDark),
				inPreview = True,
			)
	
	@objc.python_method
	def drawHints(
				self, layer, size=10000, vsize=0,
				hColor = None, 
				vColor = None, 
				inPreview = False,
			):
		
		# fallback colors:
		if not hColor:
			hColor = NSColor.colorWithRed_green_blue_alpha_(*self.rgbH, self.alphaLight)
		if not vColor:
			vColor = NSColor.colorWithRed_green_blue_alpha_(*self.rgbV, self.alphaLight)
		
		glyph = layer.parent
		if inPreview:
			shouldDisplay = True
		else:
			font = glyph.parent
			if glyph:
				# determine hinted master:
				hintMasterParameter = font.customParameters["Get Hints From Master"]
				if hintMasterParameter:
					hintMasterID = hintMasterParameter
					hintMaster = font.masters[hintMasterID]
				else:
					hintMaster = font.masters[0]
					hintMasterID = hintMaster.id
					
				# don't display in layer with hints:
				master = layer.associatedFontMaster()
				notTheHintedMaster = hintMaster != master
				# unless View > Show Hints is currently off:
				shouldDisplay = notTheHintedMaster or not Glyphs.defaults["showHints"]
					
		if shouldDisplay:
			if not inPreview:
				hintLayer = glyph.layers[hintMasterID]
				layersCompatible = glyph.mastersCompatibleForLayers_((layer, hintLayer))
			else:
				hintLayer = layer
				layersCompatible = True
				
			if layersCompatible and self.getScale() > 0.05:
				bboxLeft = layer.bounds.origin.x
				bboxBottom = layer.bounds.origin.y
				bboxHeight = layer.bounds.size.height
				bboxWidth = layer.bounds.size.width
				
				for hint in hintLayer.hints:
					if hint.type == TOPGHOST and self.pref("ghostHints"):
						originNode = hint.originNode
						if originNode:
							if inPreview:
								currentNode = originNode
							else:
								originNodeIndex = originNode.index
								originPathIndex = hintLayer.indexOfPath_(originNode.parent)
								currentNode = layer.paths[originPathIndex].nodes[originNodeIndex]
							if currentNode:
								hColor.set()
								drawRect = NSRect((bboxLeft-size, currentNode.y-20), (bboxWidth+size*2, 20))
								drawRect = self.rectifyRect(drawRect)
								NSBezierPath.fillRect_(drawRect)
				
					elif hint.type == BOTTOMGHOST and self.pref("ghostHints"):
						originNode = hint.originNode
						if originNode:
							if inPreview:
								currentNode = originNode
							else:
								originNodeIndex = originNode.index
								try:
									originPathIndex = hintLayer.indexOfObjectInShapes_(originNode.parent)
									currentNode = layer.shapes[originPathIndex].nodes[originNodeIndex]
								except:
									originPathIndex = hintLayer.indexOfPath_(originNode.parent)
									currentNode = layer.paths[originPathIndex].nodes[originNodeIndex]
							if currentNode:
								hColor.set()
								drawRect = NSRect((bboxLeft-size, currentNode.y), (bboxWidth+size*2, 20))
								drawRect = self.rectifyRect(drawRect)
								NSBezierPath.fillRect_(drawRect)
				
					elif hint.type == STEM:
						originNode = hint.originNode
						targetNode = hint.targetNode
						
						if originNode and targetNode:
							if inPreview:
								currentOrigin = originNode
								currentTarget = targetNode
							else:
								# origin:
								originNodeIndex = originNode.index
								try:
									originPathIndex = hintLayer.indexOfObjectInShapes_(originNode.parent)
									currentOrigin = layer.shapes[originPathIndex].nodes[originNodeIndex]
								except:
									originPathIndex = hintLayer.indexOfPath_(originNode.parent)
									currentOrigin = layer.paths[originPathIndex].nodes[originNodeIndex]
								# target:
								targetNodeIndex = targetNode.index
								try:
									targetPathIndex = hintLayer.indexOfObjectInShapes_(targetNode.parent)
									currentTarget = layer.shapes[targetPathIndex].nodes[targetNodeIndex]
								except:
									targetPathIndex = hintLayer.indexOfPath_(targetNode.parent)
									currentTarget = layer.paths[targetPathIndex].nodes[targetNodeIndex]
							if currentOrigin and currentTarget:
								if hint.horizontal and self.pref("horizontalStemHints"):
									hColor.set()
									drawRect = NSRect((bboxLeft-size, currentOrigin.y), (bboxWidth+size*2, currentTarget.y-currentOrigin.y))
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_(drawRect)
								elif not hint.horizontal and self.pref("verticalStemHints"):
									vColor.set()
									drawRect = NSRect((currentOrigin.x, bboxBottom-size-vsize), (currentTarget.x-currentOrigin.x, bboxHeight+(size+vsize)*2))
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_(drawRect)
	
	def conditionalContextMenus(self):
		return [
		{
			'name': Glyphs.localize({
				'en': "‘Show PS Hints’ Options:", 
				'de': "Einstellungen für »PS-Hints anzeigen«:", 
				'es': "Opciones para ‘Mostrar hints PS’:", 
				'fr': "Options pour «Afficher les hints PS»:",
				}), 
			'action': None,
		},
		{
			'name': Glyphs.localize({
				'en': "Show Vertical Stem Hints",
				'de': "Senkrechte Stamm-Hints anzeigen",
				'es': "Mostrar hints verticales",
				'fr': "Afficher hints verticaux",
				}), 
			'action': self.toggleVerticalStemHints,
			'state': self.pref("verticalStemHints"),
		},
		{
			'name': Glyphs.localize({
				'en': "Show Horizontal Stem Hints",
				'de': "Waagrechte Stamm-Hints anzeigen",
				'es': "Mostrar hints horizontales",
				'fr': "Afficher hints horizontaux",
				}), 
			'action': self.toggleHorizontalStemHints,
			'state': self.pref("horizontalStemHints"),
		},
		{
			'name': Glyphs.localize({
				'en': "Show Ghost Hints",
				'de': "Ghost-Hints anzeigen",
				'es': "Mostrar ghost hints",
				'fr': "Afficher hints «ghost»",
				}), 
			'action': self.toggleGhostHints,
			'state': self.pref("ghostHints"),
		},
		]

	def toggleVerticalStemHints(self):
		self.toggleSetting("verticalStemHints")
	
	def toggleHorizontalStemHints(self):
		self.toggleSetting("horizontalStemHints")
	
	def toggleGhostHints(self):
		self.toggleSetting("ghostHints")
	
	@objc.python_method
	def toggleSetting(self, prefName):
		domain = self.domain(prefName)
		Glyphs.defaults[domain] = not bool(self.pref(prefName))
	
	def addMenuItemsForEvent_toMenu_(self, event, contextMenu):
		if self.generalContextMenus:
			setUpMenuHelper(contextMenu, self.generalContextMenus, self)
		
		newSeparator = NSMenuItem.separatorItem()
		contextMenu.addItem_(newSeparator)
		
		contextMenus = self.conditionalContextMenus()
		if contextMenus:
			setUpMenuHelper(contextMenu, contextMenus, self)
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
