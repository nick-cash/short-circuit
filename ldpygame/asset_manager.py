import pygame, os, abc
from exceptions import NotImplementedError

class AssetManager(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.cache = {}

    def get(self, name, folder=''):
        path = os.path.join(folder, name)

        if path in self.cache:
            return self.cache[path]
        else:
            obj = self.load(path)
            self.cache[path] = obj
            return obj

    @abc.abstractmethod
    def load(self, path):
        """
        Load the object and return it. Does not put in cache
        """
        raise NotImplementedError("Please implement this method")

class ImageManager(AssetManager):
    def __init__(self):
        super(ImageManager, self).__init__()

    # Provide the default folder
    def get(self, name, folder='images'):
        return super(ImageManager, self).get(name, folder)

    def load(self, path):
        return pygame.image.load(path).convert_alpha()

class FontManager(AssetManager):
    def __init__(self):
        super(FontManager, self).__init__()

    def get(self, name, size, bold=False, italic=False):
        # Check if PyGame has it loaded
        path = pygame.font.match_font(name, bold, italic)

        if path:
            return pygame.font.Font(path, size)

        # Check if we have it loaded
        path = os.path.join('fonts', name)

        if path+str(size) in self.cache:
            return self.cache[path+str(size)]

        # Load it
        return self.load(path, size)

    def load(self, path, size):
        font = pygame.font.Font(path, size)
        self.cache[path+str(size)] = font

        return font

class SoundManager():
   music_on = True
   active_song = ""
   active_loops = -1
   initialized = False
   sounds = {}

   def __init__(self, delegate):
      """ Sets up pygame mixer """

      if not self.initialized:
         pygame.mixer.pre_init(44100, -16, 2, 4096)
         pygame.mixer.init()
         pygame.mixer.set_num_channels(16)
         self.delegate = delegate
         self.initialized = True
         if self.delegate_valid():
          preenabled = self.delegate.settings.get('music.enabled')
          if preenabled is None:
            self.delegate.settings.set('music.enabled', True)
          else:
            self.music_on = preenabled

   def delegate_valid(self):
      return self.delegate is not None and hasattr(self.delegate, 'settings') and self.delegate.settings is not None

   def toggle_music(self):
      """ Designed for use as a menu callback, turns off and restarts music."""

      if self.music_on == False:
         self.music_on = True
         if self.delegate_valid():
            self.delegate.settings.set('music.enabled', self.music_on)

         if self.active_song != "":
            pygame.mixer.music.load(os.path.join("sounds", self.active_song))
            pygame.mixer.music.play(self.active_loops)
      else:
        self.music_on = False
        if self.delegate_valid():
          self.delegate.settings.set('music.enabled', self.music_on)
        pygame.mixer.music.stop()

   def stop_music(self, fadeout=0):
      """ Stop music and reset play related variables."""
      self.active_song = ""
      self.active_loops = 0

      if fadeout > 0:
         pygame.mixer.music.fadeout(fadeout)
      else:
         pygame.mixer.music.stop()

   def load_and_play_song(self, songfile, loops = -1, volume=1.0):
      """ Loads a song and sets it to play a specified number of loops.
      Empty string to stop music. -1 loops for indefinite playing. """

      if self.active_song != songfile:
         self.active_song = songfile
         self.active_loops = loops

         if self.music_on:
            pygame.mixer.music.load(os.path.join('sounds', self.active_song))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(self.active_loops)

   def load_sound(self, soundfile, folder='sounds'):
      """ Load a sound file, store it, and return the object. If it is already loaded, return that."""

      if soundfile in self.sounds.keys():
         return self.sounds[soundfile]
      else:
         sound = pygame.mixer.Sound(os.path.join(folder, soundfile))
         self.sounds[soundfile] = sound
         return sound

   def play_sound(self, soundfile, folder='sounds', volume=1.0, loop=0, maxtime_ms=0, fade_ms=0):
      """ Play a sound, load it if necessary. """

      sound = self.load_sound(soundfile, folder)
      sound.set_volume(volume)

      # Per the PyGame docs
      # Loop = number of -extra- times to play, so loop 5 means sound is played 6 times total
      # Maxtime = max number of ms to play the sound
      # Fade = Time to fade in from 0 volume to full volume
      return sound.play(loop, maxtime_ms, fade_ms)

   def stop_sound(self, soundfile, folder='sounds', fadeout=0):
      sound = self.load_sound(soundfile, folder)

      if fadeout > 0:
         sound.fadeout(fadeout)
      else:
         sound.stop()
