# Level loading code
import xml.parsers.expat, os, pygame, copy

class SpawnDef(object):
    gid = 0
    properties = {}

    def __init__(self, x, y, width, height, gid=0, properties={}):
        self.x = x + (width/2)
        self.y = y + (height/2)

        # Optional
        self.gid = gid
        self.properties = copy.copy(properties)

class RailLevel(object):
    """ Contains all information related to a level, including
    its freshly loaded state, file information, and current play information """
 
    def __init__(self, filename):
        """ Initialize and load a level object. """
        # Width in tiles
        self.width = 0

        # Height in tiles
        self.height = 0

        # Width -of- tiles
        self.tile_width = 0

        # Height -of- tiles
        self.tile_height = 0

        # Level properties
        self.properties = {}
        self.tile_properties = {}

        # Defined objects
        self.objects = []

        # Tilesets
        self.tilesets = []

        # Individual subsurfaces of the tileset keyed with gid
        self.tile_images = {}

        # Layers of tiles. 
        self.tile_layers = []
        self.rendered_tile_layers = []

        # Used as static variables for loading... don't touch
        self.loading_object = False
      
        self.loading_tileset = False
        self.tile_id = -1

        self.rect = pygame.Rect(0,0,0,0)
        self.progress = -200;
        self.x = 0
        self.y = 0
        self.ytile = 0
        ###

        self.filename = os.path.join('levels', filename + '.tmx')
        self.load()

    def load(self):
        """ Load a level file. """

        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.start_element_handler
        p.EndElementHandler = self.end_element_handler

        with open(self.filename) as f:
            p.ParseFile(f)

        # Post Processing hook
        self.post_process()

    def post_process(self):
        """ Perform any additional setup for the level after it is loaded. """
        pass

    def progress_level(self, amt, screenwidth) :
        """ Progress the level amt pixels and return object definitions of what to spawn """
        xoffset = -1 * ((self.width - screenwidth)/2)
        tospawn = []
        layerid = -1
        for layer in self.tile_layers:
            layerid += 1
            for spawndef in layer:
                if(spawndef.y >= self.progress and spawndef.y < self.progress + amt):
                    yoffset = spawndef.y-self.progress;
                    y = -32
                    if 'spawnoffset' in spawndef.properties:
                        yoffset += int(spawndef.properties['spawnoffset'])
                    if 'type' in spawndef.properties:
                        x = spawndef.x
                        instruct = {}
                        instruct['type'] = spawndef.properties['type']
                        instruct['x'] = x
                        instruct['y'] = y+yoffset
                        instruct['properties'] = spawndef.properties
                        instruct['layer'] = layerid
                        tospawn.append(instruct)
        self.progress += amt
        return tospawn

    def start_element_handler(self, name, attrs):
        """ Set level data and create relevant objects. """

        if name == 'map':
            self.width = int(attrs['width'])*int(attrs['tilewidth'])
            self.height = int(attrs['height'])*int(attrs['tileheight'])
            self.tile_width = int(attrs['tilewidth'])
            self.tile_height = int(attrs['tileheight'])

        # Add property to the most recent element's object.
        # This is relevant for the top level map and objects in object sets.
        elif name == 'property':
            if self.loading_object:
                self.objects[-1]['properties'][attrs['name']] = attrs['value']
            elif self.loading_tileset:
                self.tile_properties[self.tile_id][attrs['name']] = attrs['value']
            else:
                self.properties[attrs['name']] = attrs['value']

        elif name == 'tileset':
            attrs['tilewidth'] = int(attrs['tilewidth'])
            attrs['tileheight'] = int(attrs['tileheight'])
            attrs['firstgid'] = int(attrs['firstgid'])

            self.tilesets.append(attrs)

            self.loading_tileset = True

        elif name == 'layer':
            self.tile_layers.append([])
            self.x = 0
            self.y = 0

        # Add tile to the latest layer
        elif name == 'tile':
            if self.loading_tileset:
                self.tile_id = int(attrs['id']) + 1
                self.tile_properties[self.tile_id] = {}
                return

            gid = int(attrs['gid'])

            x = self.x
            y = self.y

            # gid of 0 is a blank square, anything else is a tile
            if gid > 0:
                spr_props = {}
                if gid in self.tile_properties.keys():
                    spr_props = self.tile_properties[gid]
                spr = SpawnDef(x, self.height - y, self.tile_width, self.tile_height, gid, spr_props)
                self.tile_layers[-1].append(spr)

            # Move offsets
            self.x += self.tile_width

            if self.x >= self.width:
                self.x = 0
                self.y += self.tile_height
                self.ytile += 1

    def end_element_handler(self, name):
        """ Pop the current element we are handling off the stack. """

        if name == 'object':
            self.loading_object = False
        elif name == 'tileset':
            self.loading_tileset = False
            self.tile_id = -1
        #elif name == 'layer':
        #   self.render_layer(-1)