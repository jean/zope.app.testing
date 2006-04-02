##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Testing helper functions

$Id$
"""
import zope.interface
from zope.component.interfaces import IDefaultViewName
from zope.publisher.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app import zapi
from zope.app.traversing.interfaces import ITraversable

def provideView(for_, type, providing, name, factory, layer=None):
    if layer is None:
        layer = type
    provideAdapter(for_, providing, factory, name, (layer,))    

def provideMultiView(for_, type, providing, name, factory, layer=None):
    if layer is None:
        layer = type
    provideAdapter(for_[0], providing, factory, name, tuple(for_[1:])+(layer,))

def browserView(for_, name, factory, layer=IDefaultBrowserLayer,
                providing=zope.interface.Interface):
    """Define a global browser view
    """
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    provideAdapter(for_, providing, factory, name, (layer,))

def browserViewProviding(for_, factory, providing, layer=IDefaultBrowserLayer):
    """Define a view providing a particular interface."""
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    return browserView(for_, '', factory, layer, providing)

def browserResource(name, factory, layer=IDefaultBrowserLayer,
                    providing=zope.interface.Interface):
    """Define a global browser view
    """
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    provideAdapter((layer,), providing, factory, name)

def setDefaultViewName(for_, name, layer=IDefaultBrowserLayer,
                       type=IBrowserRequest):
    if layer is None:
        layer = type
    gsm = zapi.getGlobalSiteManager()
    gsm.provideAdapter((for_, layer), IDefaultViewName, '', name)

stypes = list, tuple
def provideAdapter(required, provided, factory, name='', with=()):
    if isinstance(factory, (list, tuple)):
        raise ValueError("Factory cannot be a list or tuple")
    gsm = zapi.getGlobalSiteManager()

    if with:
        required = (required, ) + tuple(with)
    elif not isinstance(required, stypes):
        required = (required,)

    gsm.registerAdapter(factory, required, provided, name)

def subscribe(required, provided, factory):
    gsm = zapi.getGlobalSiteManager()
    if provided is None:
        gsm.registerHandler(factory, required)
    else:
        gsm.registerSubscriptionAdapter(factory, required, provided)
        

def provideUtility(provided, component, name=''):
    gsm = zapi.getGlobalSiteManager()
    gsm.registerUtility(component, provided, name)

def unprovideUtility(provided, name=''):
    gsm = zapi.getGlobalSiteManager()
    gsm.provideAdapter((), provided, name, None)

def provideNamespaceHandler(name, handler):
    provideAdapter(None, ITraversable, handler, name=name)
    provideView(None, None, ITraversable, name, handler)


# BBB: Deprecated. Gone in 3.3.
from zope.deprecation import deprecated

def provideService(name, service, interface=None):
    services = zapi.getGlobalServices()
    if interface is not None:
        services.defineService(name, interface)
    services.provideService(name, service)
    
deprecated('provideService',
           'The concept of services has been removed. Use utilities instead. '
           'The reference will be gone in 3.3.')

deprecated('handle',
           'The handle(required, handler) function as a shorter spelling of '
           'subscribe(required, None, handler) has been deprecated to avoid '
           'nomenclature confusion with zope.component.handle.')
