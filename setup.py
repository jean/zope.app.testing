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
"""Setting up an environment for testing context-dependent objects

$Id$
"""
import zope.component
import zope.interface
from zope.app import zapi
from zope.app.testing import ztapi
from zope.interface import classImplements


#############################################################################
# BBB: Goes away in 3.3

from zope.component.bbb.service import IService
from zope.app.site.interfaces import ISimpleService
from zope.app.component.site import UtilityRegistration

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

#############################################################################

#------------------------------------------------------------------------
# Annotations
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.annotation.interfaces import IAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable
def setUpAnnotations():
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)

#------------------------------------------------------------------------
# Dependencies
from zope.app.dependable import Dependable
from zope.app.dependable.interfaces import IDependable
def setUpDependable():
    ztapi.provideAdapter(IAttributeAnnotatable, IDependable,
                         Dependable)

#------------------------------------------------------------------------
# Traversal
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from zope.app.container.traversal import ContainerTraversable
from zope.app.container.interfaces import ISimpleReadContainer
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import Traverser, RootPhysicallyLocatable
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.traversing.namespace import etc

def setUpTraversal():
    from zope.app.traversing.browser import SiteAbsoluteURL, AbsoluteURL

    ztapi.provideAdapter(None, ITraverser, Traverser)
    ztapi.provideAdapter(None, ITraversable, DefaultTraversable)

    ztapi.provideAdapter(
        ISimpleReadContainer, ITraversable, ContainerTraversable)
    ztapi.provideAdapter(
        None, IPhysicallyLocatable, LocationPhysicallyLocatable)
    ztapi.provideAdapter(
        IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

    # set up etc namespace
    ztapi.provideAdapter(None, ITraversable, etc, name="etc")
    ztapi.provideView(None, None, ITraversable, "etc", etc)

    ztapi.browserView(None, "absolute_url", AbsoluteURL)
    ztapi.browserView(IContainmentRoot, "absolute_url", SiteAbsoluteURL)

    ztapi.browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
    ztapi.browserView(IContainmentRoot, '', SiteAbsoluteURL,
                      providing=IAbsoluteURL)


#------------------------------------------------------------------------
# ISiteManager lookup
from zope.app.component.site import SiteManagerAdapter
from zope.component.interfaces import ISiteManager
from zope.interface import Interface
def setUpSiteManagerLookup():
    ztapi.provideAdapter(Interface, ISiteManager, SiteManagerAdapter)

#------------------------------------------------------------------------
# Placeful setup
import zope.app.component.hooks
from zope.app.testing.placelesssetup import setUp as placelessSetUp
from zope.app.testing.placelesssetup import tearDown as placelessTearDown
def placefulSetUp(site=False):
    placelessSetUp()
    zope.app.component.hooks.setHooks()
    setUpAnnotations()
    setUpDependable()
    setUpTraversal()
    setUpSiteManagerLookup()

    if site:
        site = rootFolder()
        createSiteManager(site, setsite=True)
        return site

from zope.app.component.hooks import setSite
def placefulTearDown():
    placelessTearDown()
    zope.app.component.hooks.resetHooks()
    setSite()

#------------------------------------------------------------------------
# Sample Folder Creation
from zope.app.folder import Folder, rootFolder
def buildSampleFolderTree():
    # set up a reasonably complex folder structure
    #
    #     ____________ rootFolder ____________
    #    /                                    \
    # folder1 __________________            folder2
    #   |                       \             |
    # folder1_1 ____           folder1_2    folder2_1
    #   |           \            |            |
    # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1

    root = rootFolder()
    root['folder1'] = Folder()
    root['folder1']['folder1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_2'] = Folder()
    root['folder1']['folder1_2'] = Folder()
    root['folder1']['folder1_2']['folder1_2_1'] = Folder()
    root['folder2'] = Folder()
    root['folder2']['folder2_1'] = Folder()
    root['folder2']['folder2_1']['folder2_1_1'] = Folder()

    return root


#------------------------------------------------------------------------
# Sample Folder Creation
from zope.app.component.site import LocalSiteManager
from zope.app.component.interfaces import ISite
def createSiteManager(folder, setsite=False):
    if not ISite.providedBy(folder):
        folder.setSiteManager(LocalSiteManager(folder))
    if setsite:
        setSite(folder)
    return zapi.traverse(folder, "++etc++site")


#------------------------------------------------------------------------
# Local Utility Addition
from zope.app.component.site import UtilityRegistration
from zope.app.component.interfaces.registration import ActiveStatus
def addUtility(sitemanager, name, iface, utility, suffix=''):
    """Add a utility to a site manager

    This utility is useful for tests that need to set up utilities.
    """    
    folder_name = (name or (iface.__name__ + 'Utility')) + suffix
    default = zapi.traverse(sitemanager, 'default')
    default[folder_name] = utility
    registration = UtilityRegistration(name, iface, default[folder_name])
    key = default.registrationManager.addRegistration(registration)
    zapi.traverse(default.registrationManager, key).status = ActiveStatus
    return default[folder_name]
