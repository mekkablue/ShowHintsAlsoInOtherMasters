# encoding: utf-8

############################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
############################################################################################

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from AppKit import NSRect

class ShowHintsAlsoInOtherMasters(ReporterPlugin):

	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'PS Hints Also in Other Masters',
			'de': u'PS-Hints auch in anderen Mastern',
			'fr': u'hints PS aussi dans les autres masters',
			'es': u'hints PS también en los otros masters'
		})
	
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
		
	def background(self, layer):
		# determine current master:
		master = layer.associatedFontMaster()
		
		# determine hinted master:
		glyph = layer.parent
		if glyph:
			font = glyph.parent
			hintMasterID = font.customParameters["Get Hints From Master"]
			if hintMasterID:
				hintMaster = font.masters[hintMasterID]
			else:
				hintMaster = font.masters[0]
				hintMasterID = hintMaster.id
			
			if hintMaster != master or not Glyphs.defaults["showHints"]:
				hintLayer = glyph.layers[hintMasterID]
				layersCompatible = glyph.mastersCompatibleForLayers_((layer, hintLayer))
				
				if not layersCompatible:
					pass # display a warning text
				else:
					if self.getScale() > 0.1:
						# set drawing color
						hColor = NSColor.colorWithRed_green_blue_alpha_(0.1, 0.5, 0.8, 0.2)
						vColor = NSColor.colorWithRed_green_blue_alpha_(0.8, 0.5, 0.1, 0.2)
						size = 10000
				
						for hint in hintLayer.hints:
							if hint.type == TOPGHOST:
								originNode = hint.originNode
								originNodeIndex = originNode.index
								originPathIndex = hintLayer.indexOfPath_(originNode.parent)
								currentNode = layer.paths[originPathIndex].nodes[originNodeIndex]
								if currentNode:
									hColor.set()
									drawRect = NSRect( (-size, currentNode.y-20), (size*2, 20) )
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_( drawRect )
						
							elif hint.type == BOTTOMGHOST:
								originNode = hint.originNode
								originNodeIndex = originNode.index
								originPathIndex = hintLayer.indexOfPath_(originNode.parent)
								currentNode = layer.paths[originPathIndex].nodes[originNodeIndex]
								if currentNode:
									hColor.set()
									drawRect = NSRect( (-size, currentNode.y), (size*2, 20) )
									drawRect = self.rectifyRect(drawRect)
									NSBezierPath.fillRect_( drawRect )
						
							elif hint.type == STEM:
								originNode = hint.originNode
								originNodeIndex = originNode.index
								originPathIndex = hintLayer.indexOfPath_(originNode.parent)
								currentOrigin = layer.paths[originPathIndex].nodes[originNodeIndex]
						
								targetNode = hint.targetNode
								targetNodeIndex = targetNode.index
								targetPathIndex = hintLayer.indexOfPath_(targetNode.parent)
								currentTarget = layer.paths[targetPathIndex].nodes[targetNodeIndex]
						
								if currentOrigin and currentTarget:
									if hint.horizontal:
										hColor.set()
										drawRect = NSRect( (-size, currentOrigin.y), (size*2, currentTarget.y-currentOrigin.y) )
										drawRect = self.rectifyRect(drawRect)
									else:
										vColor.set()
										drawRect = NSRect( (currentOrigin.x, -size), (currentTarget.x-currentOrigin.x, size*2) )
										drawRect = self.rectifyRect(drawRect)
										
									NSBezierPath.fillRect_( drawRect )
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
