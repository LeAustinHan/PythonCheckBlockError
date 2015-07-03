#!/usr/bin/env python
#coding=utf-8

__author__ = 'LeAustinHan'

class HHBlockVo(object):
	"""docstring for HHBlockVo"""
	def __init__(self):
		self._blockType = 0;
		self._startLine = 0;
		self._endLine  = 0;

	def set_startLine(self,startLine):
		self._startLine = startLine;
	def get_startLine(self):
		return  self._startLine

	def set_endLine(self,endLine):
		self._endLine = endLine;
	def get_endLine(self):
		return  self._endLine
#blockType  0 普通block   animationBlock  1
	def set_blockType(self,blockType):
		self._blockType = blockType;
	def get_blockType(self):
		return  self._blockType