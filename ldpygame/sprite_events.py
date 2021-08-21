from event_responder import EventResponder

class RectEventResponder(EventResponder):
  def __init__(self, callback, rect, type='RectEventResponder'):
    super(RectEventResponder, self).__init__(EventResponder.RepeatsNever, callback, type)
    self.rect = rect

    def responds_to_event(self, event):
        return EventResponder.responds_to_event(self, event) and self.rect == event.args

class SpriteWillLeaveMinXEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteWillLeaveMinXEventResponder, self).__init__(callback, rect, 'SpriteWillLeaveEventResponder-minX')

class SpriteWillLeaveMaxXEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteWillLeaveMaxXEventResponder, self).__init__(callback, rect, 'SpriteWillLeaveEventResponder-maxX')

class SpriteWillLeaveMaxYEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteWillLeaveMaxYEventResponder, self).__init__(callback, rect, 'SpriteWillLeaveEventResponder-maxY')

class SpriteWillLeaveMinYEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteWillLeaveMinYEventResponder, self).__init__(callback, rect, 'SpriteWillLeaveEventResponder-minY')

class SpriteDidLeaveMinXEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteDidLeaveMinXEventResponder, self).__init__(callback, rect, 'SpriteDidLeaveEventResponder-minX')

class SpriteDidLeaveMaxXEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteDidLeaveMaxXEventResponder, self).__init__(callback, rect, 'SpriteDidLeaveEventResponder-maxX')

class SpriteDidLeaveMaxYEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteDidLeaveMaxYEventResponder, self).__init__(callback, rect, 'SpriteDidLeaveEventResponder-maxY')

class SpriteDidLeaveMinYEventResponder(RectEventResponder):
   def __init__(self, callback, rect):
        super(SpriteDidLeaveMinYEventResponder, self).__init__(callback, rect, 'SpriteDidLeaveEventResponder-minY')

class SpriteEvent(object):
    def __init__(self, type, sprite, *args):
        self.type = type
        self.sprite = sprite
        self.args = args