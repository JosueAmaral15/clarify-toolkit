#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation module for Clarify.

Provides translation services using various providers.
"""

from .google_translate import GoogleTranslateAPI

__all__ = [
    'GoogleTranslateAPI'
]