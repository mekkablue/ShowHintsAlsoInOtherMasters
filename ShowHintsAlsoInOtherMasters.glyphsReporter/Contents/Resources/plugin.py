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

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'PS Hints Also in Other Masters',
			'de': u'PS-Hints auch in anderen Mastern',
			'fr': u'hints PS aussi dans les autres masters',
			'es': u'hints PS también en los otros masters'
		})
		
		Glyphs.registerDefault("com.mekkablue.ShowHintsAlsoInOtherMasters.verticalStemHints", True)
		Glyphs.registerDefault("com.mekkablue.ShowHintsAlsoInOtherMasters.horizontalStemHints", True)
		Glyphs.registerDefault("com.mekkablue.ShowHintsAlsoInOtherMasters.ghostHints", True)
		
	
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
					self.drawHints( layer )
	
	@objc.python_method
	def preview(self, layer):
		if not Glyphs.defaults["GSPreview_Black"]:
			# white background:
			self.drawHints(
				layer, size=20, vsize=5000,
				# hColor = NSColor.colorWithRed_green_blue_alpha_(0.1, 0.5, 0.8, 0.2), 
				# vColor = NSColor.colorWithRed_green_blue_alpha_(0.8, 0.5, 0.1, 0.2), 
				inPreview = True,
			)
		else:
			# black background:
			self.drawHints(
				layer, size=20, vsize=5000,
				hColor = NSColor.colorWithRed_green_blue_alpha_(0.1, 0.5, 0.8, 0.6),
				vColor = NSColor.colorWithRed_green_blue_alpha_(0.8, 0.5, 0.1, 0.6),
				inPreview = True,
			)
	
	@objc.python_method
	def drawHints(
				self, layer, size=10000, vsize=0,
				hColor = NSColor.colorWithRed_green_blue_alpha_(0.1, 0.5, 0.8, 0.2), 
				vColor = NSColor.colorWithRed_green_blue_alpha_(0.8, 0.5, 0.1, 0.2), 
				inPreview = False,
			):
		
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
				
			if layersCompatible:
				if self.getScale() > 0.05:
					bboxLeft = layer.bounds.origin.x
					bboxBottom = layer.bounds.origin.y
					bboxHeight = layer.bounds.size.height
					bboxWidth = layer.bounds.size.width
					
					for hint in hintLayer.hints:
						if hint.type == TOPGHOST and Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.ghostHints" ]:
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
									drawRect = NSRect( (bboxLeft-size, currentNode.y-20), (bboxWidth+size*2, 20) )
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_( drawRect )
					
						elif hint.type == BOTTOMGHOST and Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.ghostHints" ]:
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
									drawRect = NSRect( (bboxLeft-size, currentNode.y), (bboxWidth+size*2, 20) )
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_( drawRect )
					
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
									originPathIndex = hintLayer.indexOfPath_(originNode.parent)
									currentOrigin = layer.paths[originPathIndex].nodes[originNodeIndex]
									# target:
									targetNodeIndex = targetNode.index
									targetPathIndex = hintLayer.indexOfPath_(targetNode.parent)
									currentTarget = layer.paths[targetPathIndex].nodes[targetNodeIndex]
								if currentOrigin and currentTarget:
									if hint.horizontal and Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.horizontalStemHints" ]:
										hColor.set()
										drawRect = NSRect( (bboxLeft-size, currentOrigin.y), (bboxWidth+size*2, currentTarget.y-currentOrigin.y) )
										drawRect = self.rectifyRect(drawRect)
										NSBezierPath.fillRect_( drawRect )
									elif not hint.horizontal and Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.verticalStemHints" ]:
										vColor.set()
										drawRect = NSRect( (currentOrigin.x, bboxBottom-size-vsize), (currentTarget.x-currentOrigin.x, bboxHeight+(size+vsize)*2) )
										drawRect = self.rectifyRect(drawRect)
										NSBezierPath.fillRect_( drawRect )
	
	def conditionalContextMenus(self):
		return [
		{
			'name': Glyphs.localize({
				'en': u"‘Show PS Hints’ Options:", 
				'de': u"Einstellungen für »PS-Hints anzeigen«:", 
				'es': u"Opciones para ‘Mostrar hints PS’:", 
				'fr': u"Options pour «Afficher les hints PS»:",
				}), 
			'action': None,
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Vertical Stem Hints",
				'de': u"Senkrechte Stamm-Hints anzeigen",
				'es': u"Mostrar hints verticales",
				'fr': u"Afficher hints verticaux",
				}), 
			'action': self.toggleVerticalStemHints,
			'state': Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.verticalStemHints" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Horizontal Stem Hints",
				'de': u"Waagrechte Stamm-Hints anzeigen",
				'es': u"Mostrar hints horizontales",
				'fr': u"Afficher hints horizontaux",
				}), 
			'action': self.toggleHorizontalStemHints,
			'state': Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.horizontalStemHints" ],
		},
		{
			'name': Glyphs.localize({
				'en': u"Show Ghost Hints",
				'de': u"Ghost-Hints anzeigen",
				'es': u"Mostrar ghost hints",
				'fr': u"Afficher hints «ghost»",
				}), 
			'action': self.toggleGhostHints,
			'state': Glyphs.defaults[ "com.mekkablue.ShowHintsAlsoInOtherMasters.ghostHints" ],
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
		pref = "com.mekkablue.ShowHintsAlsoInOtherMasters.%s" % prefName
		Glyphs.defaults[pref] = not bool(Glyphs.defaults[pref])
	
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
