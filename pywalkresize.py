# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading
import gettext
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk,GLib,Gio,GdkPixbuf,Gdk

pictures         = [i.get_name() for i in GdkPixbuf.Pixbuf.get_formats()]+["jpg"]
imagemagik_exe   = ".\ImageMagick-7.0.9-21-portable-Q16-x86\convert.exe"
authors_         = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
version_         = "1.0"
copyright_       = "Copyright © 2019 Youssef Sourani"
website_         = "https://github.com/yucefsourani/pywalkresize"
translators_     = ("yucef sourani Arabic")
appname          = "PyWalkResize"
appwindowtitle   = "PyWalkResize"
appid            = "com.github.yucefsourani.pywalkresize"
icon_            = "com.github.yucefsourani.pywalkresize.png"

def get_correct_path(relative_path):
    if getattr(sys, 'frozen',False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if sys.platform.startswith('win'):
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang
is_pyinstaller = getattr(sys, 'frozen',False) and hasattr(sys, '_MEIPASS')
if   is_pyinstaller:
    ld = get_correct_path('locale')
else:
    exedir = os.path.dirname(sys.argv[0])
    ld = os.path.join(exedir,'..', 'share', 'locale')
    if not os.path.exists(ld):
        ld = os.path.join(exedir, 'locale')
gettext.install('pywalkresize', localedir=ld)
comments_        = _("A program for resizing images \nbut without any guarantee \nSee the GNU General Public License for more details")


MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">app.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""

css = b"""
        .h1 {
            font-size: 24px;
        }
        .h2 {
            font-weight: 300;
            font-size: 18px;
        }
        .h3 {
            font-size: 11px;
        }
        .h4 {
            color: alpha (@text_color, 0.7);
            font-weight: bold;
            text-shadow: 0 1px @text_shadow_color;
        }
        .h4 {
            padding-bottom: 6px;
            padding-top: 6px;
        }
        """

    
class Yes_Or_No(Gtk.MessageDialog):
    def __init__(self,msg,parent=None):
        Gtk.MessageDialog.__init__(self,buttons = Gtk.ButtonsType.OK_CANCEL)
        self.props.message_type = Gtk.MessageType.QUESTION
        self.props.text         = msg
        self.p=parent
        if self.p != None:
            self.parent=self.p
            self.set_transient_for(self.p)
            self.set_modal(True)
            self.p.set_sensitive(False)
        else:
            self.set_position(Gtk.WindowPosition.CENTER)
            
    def check(self):
        rrun = self.run()
        if rrun == Gtk.ResponseType.OK:
            self.destroy()
            if self.p != None:
                self.p.set_sensitive(True)
            return True
        else:
            if self.p != None:
                self.p.set_sensitive(True)
            self.destroy()
            return False
            
def resize_and_save(textview,image,saveas,width,height,ignore_aspect_ration):
    try:
        im = GdkPixbuf.Pixbuf.new_from_file_at_scale(image,width,height,ignore_aspect_ration)
        type_ = os.path.splitext(saveas)[-1][1:].lower()
        if type_ == "jpg":
            type_ = "jpeg"
        if not im.savev(saveas,type_,[],[]):
            GLib.idle_add(textview.in_text,"Resize {} Faild.".format(image))
            return False
    except Exception as e:
        print("ERROR: {}.\nResize: {} Faild".format(e,image))
        GLib.idle_add(textview.in_text,"Resize: {} Faild".format(image))
        return False
    print(saveas)
    GLib.idle_add(textview.in_text,"Done : {} .".format(saveas))
    return saveas
        
"""def main_s(location,width,height,gtk=True,ignore_aspect_ration=False): #Ignore Aspect Ratio
    if ignore_aspect_ration:
        convert = str(width)+"x"+str(height)+"!"
    else:
        conver = str(width)+"x"+str(height)
    for l in os.listdir(location):
        ll = os.path.join(location,l)
        if os.path.isfile(ll) and any([True for i in pictures if ll.lower().endswith(i)]):
            new_l = os.path.join(location,"L_result_"+str(width)+"x"+str(height))
            os.makedirs(new_l,exist_ok=True)
            if gtk:
                check = resize_and_save(ll,os.path.join(new_l,l),width,height,ignore_aspect_ration)
            else:
                check = subprocess.call("{} {} -resize {} {} ".format(imagemagik_exe,ll,convert,os.path.join(new_l,l)),shell=True)"""

def main_walk(break_,textview,spinner,button,location,width,height,gtk=True,ignore_aspect_ration=False): #Ignore Aspect Ratio
    if ignore_aspect_ration:
        convert = str(width)+"x"+str(height)+"!"
    else:
        convert = str(width)+"x"+str(height)
    GLib.idle_add(spinner.start)
    GLib.idle_add(button.set_sensitive,False)
    for dirname,folders,files  in os.walk(location):
        if break_[0]:
            return 
        if "L_result_" in dirname:
            continue
        for file_ in files:
            if break_[0]:
                return
            ll = os.path.join(dirname,file_)
            if os.path.isfile(ll) and any([True for i in pictures if ll.lower().endswith(i.lower())]):
                new_l = os.path.join(dirname,"L_result_"+str(width)+"x"+str(height))
                os.makedirs(new_l,exist_ok=True)
                if gtk:
                    check = resize_and_save(textview,ll,os.path.normpath(os.path.join(new_l,file_)),width,height,ignore_aspect_ration)
                else:
                    check = subprocess.call("{} {} -resize {} {} ".format(imagemagik_exe,ll,convert,os.path.join(new_l,file_)),shell=True)
    GLib.idle_add(spinner.stop)
    GLib.idle_add(button.set_sensitive,True)


#main_walk("C:\\Users\\yucef\\Pictures","800","600",True,False)

class RunTextView(Gtk.ScrolledWindow):
    def __init__(self,end="\n\n",
                 editable=False,
                 cursor_visible=False,
                 justification=Gtk.Justification.LEFT,
                 wrap_mode=Gtk.WrapMode.CHAR):
        Gtk.ScrolledWindow.__init__(self)
        self.end             = end
        self.editable        = editable
        self.cursor_visible  = cursor_visible
        self.justification   = justification
        self.wrap_mode       = wrap_mode
        
        self.t = Gtk.TextView(editable=self.editable,cursor_visible=self.cursor_visible,justification=self.justification,\
        wrap_mode=self.wrap_mode)
        self.buffer = self.t.get_buffer()
        
        self.add(self.t)
        self.t.connect("size-allocate", self._autoscroll)
        
    def _autoscroll(self,widget,rec):
        adj = self.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        
    def in_text(self,line):
        line = line+self.end
        self.buffer.insert_at_cursor(line,len(line))

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if icon_:
            self.set_icon(GdkPixbuf.Pixbuf.new_from_file(icon_))
        self.set_size_request(800, 600)
        #self.set_resizable(False)
        self.set_border_width(10)
        self.break_=[False]

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self.__t = False
        self.mainvbox     = Gtk.VBox(spacing=20)
        self.mainhbox     = Gtk.HBox(spacing=20)
        
        self.fvbox = Gtk.VBox(spacing=10)
        self.svbox = Gtk.VBox(spacing=10)
        self.fvbox.set_homogeneous(True)
        self.svbox.set_homogeneous(True)
        
    
        
        self.choicefolder_label = Gtk.Label()
        self.choicefolder_label.get_style_context().add_class("h2")
        self.choicefolder_label.set_label(_("Select Folder"))
        self.folder = "file:///"+GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES )
        self.choicefolder = Gtk.FileChooserButton()
        self.choicefolder.props.action = Gtk.FileChooserAction(2)
        self.choicefolder.set_uri(self.folder)
        self.fvbox.pack_start(self.choicefolder_label,False,False,0)
        self.svbox.pack_start(self.choicefolder,False,False,0)


        self.aspect_ration_switch_label = Gtk.Label()
        self.aspect_ration_switch_label.get_style_context().add_class("h2")
        self.aspect_ration_switch_label.set_label(_("Enable Aspect Ratio"))
        self.aspect_ration_switch = Gtk.Switch()
        self.grid_aspect_ration_switch = Gtk.Grid()
        self.grid_aspect_ration_switch.add(self.aspect_ration_switch)
        self.fvbox.pack_start(self.aspect_ration_switch_label,False,False,0)
        self.svbox.pack_start(self.grid_aspect_ration_switch,False,False,0)
        

        self.width_spin_hbox  = Gtk.HBox(spacing=10)
        width_spin_hbox       = Gtk.Label()
        width_spin_hbox.get_style_context().add_class("h2")
        width_spin_hbox.set_label(_("Width"))
        width_adjustment = Gtk.Adjustment(value=200,lower=10,upper=3000,page_size=1,step_increment=1, page_increment=0)
        self.width_spin  = Gtk.SpinButton(max_width_chars=2,value=200,adjustment=width_adjustment) 
        self.width_spin_hbox.pack_start(width_spin_hbox,True,False,0)
        self.width_spin_hbox.pack_start(self.width_spin,True,False,0)
        
        
        
        self.height_spin_hbox  = Gtk.HBox(spacing=10)
        height_spin_label      = Gtk.Label()
        height_spin_label.get_style_context().add_class("h2")
        height_spin_label.set_label(_("Height"))
        height_adjustment = Gtk.Adjustment(value=200,lower=10,upper=3000,page_size=1,step_increment=1, page_increment=0)
        self.height_spin  = Gtk.SpinButton(max_width_chars=2,value=200,adjustment=height_adjustment) 
        self.height_spin_hbox.pack_start(height_spin_label,True,False,0)
        self.height_spin_hbox.pack_start(self.height_spin,True,False,0)
        
        

        self.start_button = Gtk.Button()
        self.start_button.get_style_context().add_class("suggested-action")
        self.start_button.set_label(_("Run"))
        self.start_button.connect("clicked",self.__on_button_clicked)

        
        self.spinner  = Gtk.Spinner()
        self.textview = RunTextView()

        self.fvbox.pack_start(self.width_spin_hbox,True,False,0)
        self.svbox.pack_start(self.height_spin_hbox,True,False,0)
        self.mainhbox.pack_start(self.fvbox,True,False,0)
        self.mainhbox.pack_start(self.svbox,True,False,0)
        self.mainvbox.pack_start(self.mainhbox,False,False,0)
        self.mainvbox.pack_start(self.start_button,False,False,0)
        self.mainvbox.pack_start(self.spinner,False,False,0)
        self.mainvbox.pack_start(self.textview,True,True,0)
        self.add(self.mainvbox)
        self.show_all()

    def __on_button_clicked(self,button):
        uri = self.choicefolder.get_uri()
        if not uri:
            return
            
        y_or_n = Yes_Or_No(_("Do you want to continue ?"),self)
        y_or_n.get_message_area().get_children()[0].get_style_context().add_class("h1")
        if not y_or_n.check():
            return
        self.__start(uri[8:])
        
    def __start(self,uri):
        self.__t = threading.Thread(target = main_walk,args = (self.break_,self.textview,
                                                       self.spinner,
                                                       self.start_button,
                                                       uri,
                                                       self.width_spin.get_value_as_int(),
                                                       self.height_spin.get_value_as_int(),
                                                       True,
                                                       self.aspect_ration_switch.get_state())).start()
        


class App(Gtk.Application):
    def __init__(self ,*args, **kwargs):
        super().__init__(
        application_id=appid,
        flags=Gio.ApplicationFlags.FLAGS_NONE,
        **kwargs
        )
        self.appwindow = None
        
    def do_startup(self):
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_app_menu(builder.get_object("app-menu"))
        
    def do_activate(self):
        if not self.appwindow:
            self.appwindow = AppWindow(application=self, title=appwindowtitle)
            self.appwindow.connect("delete-event",self.on_quit)
        self.appwindow.present()

    def on_quit(self, action, param):
        if self.appwindow:
            self.appwindow.break_[0]=True
        self.quit()

    def on_about(self,a,p):
        about = Gtk.AboutDialog(parent=self.appwindow,transient_for=self.appwindow, modal=True)
        about.set_program_name(appname)
        about.set_version(version_)
        about.set_copyright(copyright_)
        about.set_comments(comments_)
        about.set_website(website_)
        if icon_:
            logo_=GdkPixbuf.Pixbuf.new_from_file(icon_)
            about.set_logo(logo_)
        about.set_authors(authors_)
        about.set_license_type(Gtk.License.GPL_3_0)
        if translators_ != "translator-credits":
            about.set_translator_credits(translators_)
        about.run()
        about.destroy()

def main():
    app = App()
    app.run(sys.argv)
if __name__ == "__main__":
    main()
