import batFramework as bf
import pygame


class DarkStyle(bf.gui.Style):

    def apply(self, w: bf.gui.Widget):
        if isinstance(w, bf.gui.Shape):
            if isinstance(w, bf.gui.Image):
                return
            w.set_outline_color("white")
            w.set_outline_width(1)
            w.set_border_radius(2)
            w.set_padding(2)
            w.set_color("black")
            w.set_shadow_color(bf.color.mult(pygame.Color("white"), 0.2))

        if isinstance(w, bf.gui.InteractiveWidget):
            w.draw_focused = lambda *args: None

        if isinstance(w, bf.gui.ClickableWidget):
            w.set_unpressed_relief(0)
            w.set_pressed_relief(0)

        if isinstance(w, bf.gui.Label):
            w.set_color((0, 0, 0))
            w.set_outline_width(1)
            w.set_text_color("white")
            w.set_outline_color("white")
            w.set_alignment(bf.alignment.LEFT)
            w.set_padding((6, 4))

        if isinstance(w, bf.gui.ToolTip):
            w.set_color("black")
            w.set_text_color("white")
            w.set_outline_color("white")
            w.set_outline_width(1)
            w.set_padding(6)

        if isinstance(w, bf.gui.Button):
            w.set_color("black")
            w.set_outline_color("white")
            w.set_text_color("white")
            w.set_border_radius(4)
            w.set_outline_width(1)

        if isinstance(w, bf.gui.TextInput):
            w.set_color("black")
            w.set_outline_color("white")
            w.set_text_color("white")
            w.set_padding((6, 4))
            w.set_outline_width(1)

        if isinstance(w, (bf.gui.Toggle, bf.gui.RadioButton)):
            w.set_color("black")
            w.set_outline_color("white")
            w.set_text_color("white")
            w.set_spacing(bf.spacing.MAX)

        if isinstance(w, bf.gui.Container):
            w.set_padding(6)

        if isinstance(w, bf.gui.Selector):
            w.set_color("black")
            w.set_outline_color("white")
            w.set_text_color("white")
            w.left_indicator.set_padding(2).set_arrow_line_width(1)
            w.right_indicator.set_padding(2).set_arrow_line_width(1)

        if isinstance(w, bf.gui.Slider):
            w.set_outline_width(0)
            w.set_padding(0)
            w.set_color(None)
            w.set_clip_children(False)
            w.set_unpressed_relief(0)
            w.set_pressed_relief(0)
            w.meter.set_outline_width(1)
            w.meter.set_border_radius(4)
            w.meter.set_outline_color("white")
            w.meter.set_padding((4, 8))
            w.meter.set_clip_children(False)
            w.meter.set_color("black")
            w.meter.content.set_color("white")
            w.meter.handle.set_outline_width(1)
            w.meter.handle.set_border_radius(16)
            w.meter.handle.set_color("black")
            w.meter.handle.set_outline_color("white")
