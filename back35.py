##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Features that will be deprecated in Zope 3.5

$Id$
"""

from zope.app import zapi
import zope.interface
from zope.component.service import IService
from zope.app.site.interfaces import ISimpleService
from zope.app.component.site import UtilityRegistration
from zope.app.component.back35 import ActiveStatus

def addService(servicemanager, name, service, suffix=''):
    """Add a service to a service manager

    This utility is useful for tests that need to set up services.
    """
    # Most local services implement ISimpleService in ZCML; therefore make
    # sure we got it here as well.
    zope.interface.directlyProvides(service, ISimpleService)

    default = zapi.traverse(servicemanager, 'default')
    default[name+suffix] = service
    registration = UtilityRegistration(name, IService, service, default)
    key = default.registrationManager.addRegistration(registration)
    zapi.traverse(default.registrationManager, key).status = ActiveStatus
    return default[name+suffix]
