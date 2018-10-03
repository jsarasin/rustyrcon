import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject, GLib, Gdk, cairo, Gio


def scroll_to_textview_bottom(tv):
    model = tv.get_buffer()
    end_iter = model.get_iter_at_line(model.get_line_count()-1);
    end_mark = model.create_mark(None, end_iter, False)

    tv.scroll_to_mark(end_mark, 0.1, True, 0.0, 1.0)
    model.delete_mark(end_mark)


class BetterBuffer(Gtk.TextBuffer):
    """
    This is another layer ontop of Gtk.TextBuffer which helps to deal with fancy text.
    """
    mark_name_list = []
    last_cat = 0
    mymark = None
    bubbles = None
    owner_id = None

    def __init__(self):
        Gtk.TextBuffer.__init__(self)


    def _get_not_so_start_iter(self):
        me = self.get_start_iter()
        me.forward_char()
        if not me: raise (ValueError("Someone soiled the buffer!"))
        return me

    # def create_tag(self, tag_name, **kargs):
    #     self.create_tag(tag_name, **kargs)
        # self.create_tag("says", weight=Pango.Weight.BOLD)
        # self.create_tag("message", indent=10)
        # self.create_tag("time-sent", variant=Pango.Variant.SMALL_CAPS,
        #                 scale=0.75,
        #                 wrap_mode_set=Gtk.WrapMode.NONE)
        #
        # self.create_tag("bubble-left", paragraph_background="lightgreen",
        #                 right_margin=50)
        #
        # self.create_tag("bubble-right", justification=Gtk.Justification.RIGHT,
        #                 paragraph_background="lightblue",
        #                 left_margin=100,
        #                 direction=Gtk.TextDirection.RTL,
        #                 wrap_mode=Gtk.WrapMode.WORD_CHAR,
        #                 right_margin=0)
        # self.create_tag("highlight", background="orange");
    def get_tag(self, tag):
        return self.get_tag_table().lookup(tag)

    def apply_tag_to_mark_range(self, tag_name, start_mark, end_mark):
        if (not isinstance(start_mark, Gtk.TextMark) or not isinstance(end_mark, Gtk.TextMark)):
            raise (ValueError("Cannot apply tag to non TextMark objects"))
        mark1 = self.get_iter_at_mark(start_mark)
        mark2 = self.get_iter_at_mark(end_mark)

        self.apply_tag_by_name(tag_name, mark1, mark2)

    # def create_mark(self, name, itera, left_gravity=True):
    #     if name in self.mark_name_list and name != None:
    #         raise ValueError("You already created a mark with this name!")
    #
    #     offset = itera.get_offset()
    #
    #     new_mark = Gtk.TextBuffer.create_mark(self, name, itera, left_gravity)
    #     # new_mark.set_visible(True)
    #
    #     self.mark_name_list.append(name)
    #     return new_mark
