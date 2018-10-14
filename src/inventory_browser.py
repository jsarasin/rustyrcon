import os
import json
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio, Pango, GObject


class RustItemBrowserModel:
    def __init__(self):
        self.item_path = RustItemBrowserModel.search_item_path()
        self.items_by_category = dict()

        if self.item_path is not None:
            self.initialize_item_data()

    def initialize_item_data(self):
        files = os.listdir(str(self.item_path))

        for item in files:
            if item[-4:] == ".txt":
                definition = RustItemBrowserModel.read_item_file(self.item_path / item, just_definition=True)
                definition = definition['ItemDefinition']

                if definition['category'] not in self.items_by_category:
                    self.items_by_category[definition['category']] = []

                self.items_by_category[definition['category']].append(definition)

                assert(definition['shortname'] + ".txt" == item)

    def get_item_details(self, shortname):
        if self.item_path is not None:
            cat = RustItemBrowserModel.read_item_file(self.item_path / Path(shortname + ".txt"))
            return cat
        else:
            cat = dict()
            cat['Builtin Data'] = {'shortname':'test.cat', 'name':'Test Cat'}
            return cat

    def get_pixbuf_from_shortname(self, shortname, desired_size):
        if self.item_path is not None:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(self.item_path / shortname) + ".png", desired_size, -1, True)
        else:
            pixbuf = Gtk.IconTheme.get_default().load_icon('image-missing', desired_size, Gtk.IconLookupFlags.FORCE_SIZE)

        return pixbuf

    @staticmethod
    def search_item_path():
        shared_default = Path('/home/james/MEGAsync/Rust Server/items/')
        # linux_default = Path('~/.steam/steam/steamapps/common/Rust/Bundles/items/').expanduser()
        linux_default = Path('~/.steam/steam/steamapps/common/Rust/Bundles/items/')
        windows_default = Path('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Rust\\Bundles\\items\\')

        if os.path.isdir(str(windows_default)):
            return windows_default

        #print(os.path.isdir(linux_default))
        if os.path.isdir(shared_default):
            return shared_default

        if os.path.isdir(linux_default):
            return linux_default


        return None

    @staticmethod
    def read_item_file(filename, just_definition=False):
        def read_json_section(f):
            json_data = f.readline()
            assert(json_data == "{\n")

            while True:
                line = f.readline()
                if line == "\n":
                    break
                json_data = json_data + line

            return json.loads(json_data)

        item_file_sections = ['ItemDefinition',
                              'ItemBlueprint',
                              'ItemModMenuOption',
                              'ItemModEntity',
                              'ItemModSound',
                              'ItemModDeployable',
                              'ItemModWearable',
                              'ItemModConsume',
                              'ItemModConsumable',
                              'ItemModCookable',
                              'ItemModProjectileSpawn',
                              'ItemModRepair',
                              'ItemModContainer',
                              'ItemFootstepSounds',
                              'ItemModContainerRestriction']

        with open(str(filename),'r') as f:
            line = f.readline()
            assert(line == "This file is provided for informational purposes only. Changes aren't reflected in game.\n")
            line = f.readline()
            assert (line == "\n")
            result = dict()

            while True:
                section = f.readline()
                if just_definition:
                    if section != "ItemDefinition\n":
                        continue
                    item_definition_dict = dict()
                    item_definition_dict['ItemDefinition'] = read_json_section(f)

                    return item_definition_dict

                if section[:-1] in item_file_sections:
                    result[section[:-1]] = read_json_section(f)

                # EOF
                if section == "":
                    break

            return result


RustItemCategories = dict()
RustItemCategories[0] = "Weapons"
RustItemCategories[1] = "Buildables"
RustItemCategories[2] = "Items"
RustItemCategories[3] = "Resources"
RustItemCategories[4] = "Clothing/Armour"
RustItemCategories[5] = "Tools/Weapons"
RustItemCategories[6] = "Medical"
RustItemCategories[7] = "Food"
RustItemCategories[8] = "Ammo"
RustItemCategories[9] = "Traps"
RustItemCategories[10] = "Bullshit/Door Key Lock"
RustItemCategories[13] = "Intermediate Items"

# This is a small wrapper allow IconView which handles the correct propagation of events when this widget changes its
# side.
class FluidIconView (Gtk.IconView):
    def __init__ (self):
        Gtk.IconView.__init__ (self)
        self.connect ("size-allocate", FluidIconView.on_size_allocate)

    def do_get_preferred_width (self):
        return (0,0)

    def on_size_allocate (self, allocation):
        [self.set_columns (m) for m in [1,self.get_columns ()]]

class WindowInventoryBrowser:
    def __init__(self, as_program=False):
        self.is_program = as_program
        self.item_browser = RustItemBrowserModel()
        self.icon_views = []
        self.ignore_selection = False
        self.pixbuf_missing_image = Gtk.IconTheme.get_default().load_icon('image-missing', 64, Gtk.IconLookupFlags.FORCE_SIZE)
        self.expander_models = dict()

        self.connect_builder_objects()


        if self.item_browser.item_path is None:
            self.infobar_pathnotfound.set_visible(True)
            self.infobar_pathnotfound.set_revealed(True)

        # Build the model
        self.model = Gtk.TreeStore(int,str,str, GdkPixbuf.Pixbuf)
        for category in self.item_browser.items_by_category:
            category_iter = self.model.append(None, [int(category), RustItemCategories[category], '', None])

            for item in sorted(self.item_browser.items_by_category[category], key=lambda item: item['shortname']):
                pixbuf = self.pixbuf_missing_image
                self.model.append(category_iter, [int(item['category']),
                                                  item['shortname'],
                                                  item['displayName']['english'],
                                                  pixbuf])


        # Build the UI components for icon view
        for category in self.item_browser.items_by_category:
            expander = Gtk.Expander.new(RustItemCategories[category])
            expander.set_expanded(False)
            label_style = Gtk.RcStyle.new()
            # label_style.fg = [Gdk.Color(1.0, 0.0, 0.0)]

            # label_style.font_desc = Pango.FontDescription()
            # label_style.font_desc.set_size(200)
            label = expander.get_label_widget()
            label.modify_style(label_style)
            expander.connect('activate', self.event_expander_toggle)

            icon_view = FluidIconView()
            # icon_view.set_markup_column
            icon_view.set_text_column(2)
            icon_view.set_item_width(80)
            icon_view.set_pixbuf_column(3)
            icon_view.set_columns(0)
            icon_view.set_hexpand(True)
            this_model = self.model.filter_new(Gtk.TreePath.new_from_indices([category]))
            icon_view.set_model(this_model)
            icon_view.connect('selection-changed', self.event_iconview_selection_changed)
            self.icon_views.append(icon_view)

            expander.add(icon_view)
            self.box_iconview_categories.pack_start(expander, False, False, 0)

            self.expander_models[expander] = this_model

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Name", renderer_text, text=1)
        self.treeview_items.append_column(column_text)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Description", renderer_text, text=2)
        self.treeview_items.append_column(column_text)

        self.treeview_items.set_model(self.model)
        self.window.show_all()

    def event_iconview_selection_changed(self, iconview):
        if self.ignore_selection:
            return

        self.ignore_selection = True

        for iv in self.icon_views:
            if iv is not iconview:
                iv.unselect_all()
        self.ignore_selection = False

        treepath = iconview.get_selected_items()
        if len(treepath) == 1:
            iter = iconview.get_model().get_iter(treepath)
            self.selected_item(iconview.get_model()[iter][1])


    def event_expander_toggle(self, expander):
        self.viewport_iconview_items.get_parent().check_resize()
        model = self.expander_models[expander]

        if model is not None:
            GLib.idle_add(self.load_model_icons, expander, model)

    def load_model_icons(self, expander, model):
        iter = model.get_iter_first()

        if iter is None:
            self.expander_models[expander] = None
            return

        while True:
            pixbuf = self.item_browser.get_pixbuf_from_shortname(model[iter][1], 64)
            model[iter][3] = pixbuf

            iter = model.iter_next(iter)
            if iter is None:
                break
        self.expander_models[expander] = None

    def connect_builder_objects(self):
        builder = Gtk.Builder()
        builder.add_from_file("command_browser.glade")

        self.window = builder.get_object('window_inventory_browser')
        if self.is_program:
            self.window.connect("delete-event", self.event_window_close)
        else:
            self.window.connect("delete-event", self.event_window_close)

        self.viewport_iconview_items = builder.get_object('viewport_iconview_items')
        self.box_iconview_categories = Gtk.Box(Gtk.Orientation.VERTICAL, 5)
        self.box_iconview_categories.set_orientation(Gtk.Orientation.VERTICAL)
        self.box_iconview_categories.set_homogeneous(False)

        self.stack_viewtype = builder.get_object('stack_viewtype')
        self.radiotoolbutton_listview = builder.get_object('radiotoolbutton_listview')
        self.radiotoolbutton_listview.connect('toggled', self.viewmode_toggled)
        self.radiotoolbutton_iconview = builder.get_object('radiotoolbutton_iconview')
        self.radiotoolbutton_iconview.connect('toggled', self.viewmode_toggled)
        self.togglebutton_details = builder.get_object('togglebutton_details')
        self.togglebutton_details.connect('toggled', self.event_togglebutton_details)
        self.revealer_details = builder.get_object('revealer_details')
        self.treeview_items = builder.get_object('treeview_items')
        self.treeview_items.connect('row-activated', self.event_treeview_items_row_activated)
        self.treeview_items.connect('cursor-changed', self.event_treeview_items_changed)

        self.listbox_details = builder.get_object('listbox_details')

        self.infobar_pathnotfound = builder.get_object('infobar_pathnotfound')

        self.viewport_iconview_items.add(self.box_iconview_categories)

    def selected_item(self, shortname):
        for widget in self.listbox_details.get_children():
            widget.destroy()

        # cat = RustItemBrowser.read_item_file(self.item_browser.item_path + shortname + ".txt")
        cat = self.item_browser.get_item_details(shortname)

        for section in cat:
            if section == 'ItemDefinition':
                self.details_listbox_add_definition_section(self.listbox_details, cat)
            if section == 'ItemModProjectileSpawn':
                self.details_listbox_add_itemmodprojectilespawn_section(self.listbox_details, cat)
            if section == 'Builtin Data':
                self.details_listbox_add_buildin_data(self.listbox_details, cat)

        self.listbox_details.show_all()

    def event_treeview_items_row_activated(self, treeview, path, column):
        if path.get_depth() == 1:
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, True)
            return False


    def event_treeview_items_changed(self, treeview):
        model, iter = treeview.get_selection().get_selected()
        if iter is None:
            return

        parent_iter = model.iter_parent(iter)

        if parent_iter is None:
            return

        shortname = model[iter][1]
        self.selected_item(shortname)

    def details_listbox_add_buildin_data(self, listbox, cat):
        shortname = cat['Builtin Data']['shortname']
        name = cat['Builtin Data']['name']

        header = Gtk.Label('Builtin Data')
        row = Gtk.ListBoxRow()
        row.add(header)
        row.set_activatable(False)
        self.listbox_details.add(row)

        self.listbox_details.add(Gtk.Label(shortname))
        self.listbox_details.add(Gtk.Label(name))

    def details_listbox_add_itemmodprojectilespawn_section(self, listbox, cat):
        projectileVelocity = cat['ItemModProjectileSpawn']['projectileVelocity']
        projectileVelocitySpread = cat['ItemModProjectileSpawn']['projectileVelocitySpread']
        projectileSpread = cat['ItemModProjectileSpawn']['projectileSpread']

        header = Gtk.Label('ItemModProjectileSpawn')
        row = Gtk.ListBoxRow()
        row.add(header)
        row.set_activatable(False)

        self.listbox_details.add(row)

        self.lb_add_detail("Velocity", projectileVelocity)
        self.lb_add_detail("Spread", projectileVelocitySpread)
        self.lb_add_detail("Speed", projectileSpread)

    def details_listbox_add_definition_section(self, listbox, cat):
        name = cat['ItemDefinition']['displayName']['english']
        shortname = cat['ItemDefinition']['shortname']
        pixy = self.item_browser.get_pixbuf_from_shortname(shortname, 200)
        item_id = cat['ItemDefinition']['itemid']

        header = Gtk.Label('ItemDefinition')
        row = Gtk.ListBoxRow()
        row.add(header)
        row.set_activatable(False)

        self.listbox_details.add(row)

        self.listbox_details.add(Gtk.Image.new_from_pixbuf(pixy))
        self.lb_add_detail("Title", name)
        self.lb_add_detail("Shortname", shortname)
        self.lb_add_detail("ID", "{}".format(item_id))
        # self.listbox_details.add()
        # self.listbox_details.add()
        # self.listbox_details.add()
        # self.listbox_details.add()

    def lb_add_detail(self, key, value):
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.pack_start(Gtk.Label(key), False, True,0)
        box.pack_end(Gtk.Label(value), False, True,0)

        self.listbox_details.add(box)


    def event_togglebutton_details(self, button):
        if button.get_active():
            self.revealer_details.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
            self.revealer_details.set_reveal_child(True)
        else:
            self.revealer_details.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
            self.revealer_details.set_reveal_child(False)




    def viewmode_toggled(self, radiobutton):
        if radiobutton == self.radiotoolbutton_listview:
            self.stack_viewtype.set_visible_child_name('stackview_list')
        if radiobutton == self.radiotoolbutton_iconview:
            self.stack_viewtype.set_visible_child_name('stackview_icon')

    def event_window_close(self, window, event):
        print("sdf")
        if self.is_program:
            Gtk.main_quit()
        else:
            print("WINDOW CLOSE")
            self.window.hide()
            return True

if __name__ == '__main__':
    print("Asdf")
    settings = Gtk.Settings.get_default()
    settings.props.gtk_application_prefer_dark_theme = True

    wib = WindowInventoryBrowser(as_program=True)
    Gtk.main()
