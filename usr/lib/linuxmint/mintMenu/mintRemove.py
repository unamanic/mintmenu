#!/usr/bin/env python
from packagekit.enums import FILTER_INSTALLED

try:
     import pygtk
     pygtk.require("2.0")
except:
      pass
try:
    import sys
    import string
    import gtk
    import gtk.glade
    import os
    import commands
    import threading
    import tempfile
    import gettext

except Exception, detail:
    print detail
    sys.exit(1)

from subprocess import Popen, PIPE

gtk.gdk.threads_init()

# i18n
gettext.install("mintmenu", "/usr/share/linuxmint/locale")

class RemoveExecuter(threading.Thread):

    def __init__(self, window_id, package):
    	threading.Thread.__init__(self)
    	self.window_id = window_id
    	self.package = package
    
    def execute(self, command):
    	#print "Executing: " + command
    	os.system(command)
    	ret = commands.getoutput("echo $?")
    	return ret

    def run(self):	
    	removePackages = self.package

        from packagekit.client import PackageKitClient
        from packagekit.enums import *
        
        pk = PackageKitClient()
        
        #print '---- Remove -------'
        pk.remove_packages(removePackages)
        
    	gtk.main_quit()
    	sys.exit(0)
		
class mintRemoveWindow:

    def __init__(self, desktopFile):
    	self.desktopFile = desktopFile	
    
        #Set the Glade file
        self.gladefile = "mintRemove.glade"
        wTree = gtk.glade.XML(self.gladefile,"main_window")
    	wTree.get_widget("main_window").set_icon_from_file("icon.svg")
    	wTree.get_widget("main_window").set_title("")
    	wTree.get_widget("main_window").connect("destroy", self.giveUp)
    
    	# Get the window socket (needed for synaptic later on)
    	vbox = wTree.get_widget("vbox1")
    	socket = gtk.Socket()
    	vbox.pack_start(socket)
    	socket.show()
    	window_id = repr(socket.get_id())
            
        from packagekit.client import PackageKitClient
        from packagekit.enums import *
        
        pk = PackageKitClient()
        
        package = pk.search_file(self.desktopFile, FILTER_INSTALLED)
        print package[0]
          
        wTree.get_widget("txt_name").set_text("<big><b>" + _("Remove %s?") % package[0] + "</b></big>")
        wTree.get_widget("txt_name").set_use_markup(True)
            
        wTree.get_widget("txt_guidance").set_text(_("The following packages will be removed:"))
        
        treeview = wTree.get_widget("tree")
        column1 = gtk.TreeViewColumn(_("Packages to be removed"))
        renderer = gtk.CellRendererText()
        column1.pack_start(renderer, False)
        column1.set_attributes(renderer, text = 0)
        treeview.append_column(column1)
    
        model = gtk.ListStore(str)
        dependencies = pk.get_requires(package, FILTER_INSTALLED, True)
        for dependency in dependencies:
            model.append([dependency])
        treeview.set_model(model)
        treeview.show()        
   
        dic = {"on_remove_button_clicked" : (self.MainButtonClicked, window_id, package, wTree),
                   "on_cancel_button_clicked" : (self.giveUp) }
        wTree.signal_autoconnect(dic)
    
        wTree.get_widget("main_window").show()


    def MainButtonClicked(self, widget, window_id, package, wTree):
        wTree.get_widget("main_window").window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        wTree.get_widget("main_window").set_sensitive(False)
        executer = RemoveExecuter(window_id, package)
        executer.start()
        return True

    def giveUp(self, widget):
        gtk.main_quit()
        sys.exit(0)

if __name__ == "__main__":
    mainwin = mintRemoveWindow(sys.argv[1])
    gtk.main()
    
