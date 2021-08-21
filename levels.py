import pygame, random, abc

from ldpygame.screen import Screen
from ldpygame.sprite_events import *
from ldpygame.sprite import SpriteManager

from user_sprites import UserShip
from bhsprite import *
from enemy_sprites import *
from bhgame import BulletHellGame
from weapon_system import *
from rail_level import RailLevel
import math

class BackgroundObject(object):
    def __init__(self, bounds):
        self.bounds = bounds
        self.image = pygame.Surface(bounds)
        self.image.fill(pygame.Color(0,0,0))

    @abc.abstractmethod
    def update(self):
        """Update background objects and render to self.image"""
        raise NotImplementedError("Please implement this method")

class StarryBackground(BackgroundObject):
    def __init__(self, bounds, num_stars):
        super(StarryBackground, self).__init__(bounds)

        self.num_stars = int(num_stars)
        self.stars = {}

        for star in range(0, self.num_stars):
            x = random.randint(5,bounds[0] - 10)
            y = random.randint(5,bounds[1] - 10)

            if random.randint(1,10) == 10:
                self.spawn_starcluster((x,y))
            else:
                self.stars[(x,y)] = self.twinkle((x,y))

    def spawn_starcluster(self, center):
        pattern = random.randint(0,15)
        x = center[0]
        y = center[1]
        self.stars[center] = self.twinkle(center)
        positions = [(0,1),(0,-1),(-1,0),(1,0)]
        for bit in range(0,8):
            if( (((1<<bit)&pattern) >> bit) == 1):
                nx = positions[bit][0]
                ny = positions[bit][1]
                self.stars[(x+nx,y+ny)] = self.twinkle((x+nx,y+ny))

    def twinkle(self,position):
        c = pygame.Color(0,0,0)
        # hue and saturation, based on position.
        hsva = c.hsva
        h = 180 + (math.sin(position[0])*180)
        s = 20 + (math.sin(position[1])*20)
        # brightness
        v = random.randint(20, 100)
        c.hsva = (h,s,v,hsva[3])
        return c

    def update(self, *args):
        self.image.fill(pygame.Color(0,0,0))

        for star in self.stars:
            if random.randint(1,100) == 100:
                self.stars[star] = self.twinkle(star)

            self.image.set_at(star, self.stars[star])

class BackgroundObjectScreen(Screen):
    def __init__(self, name, size, offset=(0,0), background=None):
        super(BackgroundObjectScreen, self).__init__(name, size, offset, background)

        if isinstance(background, BackgroundObject):
            self.background_object = background
            background.update()
            self.background = self.background_object.image
        else:
            self.background_object = None

    def update(self, tick_time):
        if self.background_object:
            self.background_object.update(tick_time)
            self.background = self.background_object.image
        super(BackgroundObjectScreen, self).update(tick_time)

    # With an animated background we must redraw the entire screen every time
    def draw(self):
        # Testing dirty rects; with enough objects it seems better
        #return super(BackgroundObjectScreen, self).draw()

        self.screen_surface.blit(self.background, (0,0))
        for sprite in self.sprites:
            sprite.dirty = 1
        dirty_rects = self.sprites.draw(self.screen_surface)
        return [pygame.Rect((0,0), self.size)]

class ScoreScreen(BackgroundObjectScreen):
    def __init__(self, name, size, offset=(0,0), background=None):
        super(ScoreScreen, self).__init__(name, size, offset, background)
        self.displays = SpriteManager()

        s = Scoreboard(pygame.Rect((525,5), (50, 20)), self.displays,
                       "Score: {}", BulletHellGame.active_game.fonts.get("Helvetica", 20))

    def update(self, tick_time):
        super(ScoreScreen, self).update(tick_time)
        self.displays.update(tick_time)

    def draw(self):
        super(ScoreScreen, self).draw()
        self.displays.draw(self.screen_surface)
        return [pygame.Rect((0,0), self.size)]

class GameLevel(ScoreScreen):
    def __init__(self, name, size, offset=(0,0), background=None):
        super(GameLevel, self).__init__(name, size, offset, background)
        self.trajectories = []
        self.player_bullets = SpriteManager()
        self.enemy_bullets = SpriteManager()

        self.ship = self.make_ship()
        self.fuel_display = None

        SideBar(pygame.Rect((500,0), (200, 700)), self.displays,
                    BulletHellGame.active_game.fonts.get("Helvetica", 20))

        # Test for level loading
        self.level = RailLevel('level1')
        self.level_advancement = 10

    def activate(self):
        if not self.fuel_display:
            self.fuel_display = FuelDisplay(pygame.Rect((525,30), (200, 15)), self.displays,
                                            BulletHellGame.active_game.fonts.get("Helvetica", 20))

        BulletHellGame.active_game.sounds.load_and_play_song('FranklinWebberMusic/ddd-printer.ogg', volume=0.2)
        return super(GameLevel, self).activate()

    def draw(self):
        self.screen_surface.blit(self.background, (0,0))

        # make sure we repaint them every screeen since we have an animated background
        for sprite in self.sprites:
            sprite.dirty = 1

        self.player_bullets.draw(self.screen_surface)
        self.sprites.draw(self.screen_surface)
        self.enemy_bullets.draw(self.screen_surface)
        self.displays.draw(self.screen_surface)

        return [pygame.Rect((0,0), self.size)]

    def make_ship(self):
        ship = UserShip(pygame.Rect((250,500), (30, 30)),
                                 pygame.Rect((0,0), self.size),
                                 self.sprites, self.player_bullets,
                                 BulletHellGame.active_game.images.get('ship.png'),
                                 frame_delay_ms=80,
                                 num_frames = 5)
        ship.enable_horz_tiltmode()
        ship.add_event_responders(self.event_manager)
        return ship

    def update_trajectories(self, tick_time):
        for trajectory in self.trajectories:
            trajectory.tick_trajectory(tick_time)

    def update(self, tick_time):
        super(GameLevel, self).update(tick_time)

        self.update_trajectories(tick_time)
        self.player_bullets.update(tick_time)
        self.enemy_bullets.update(tick_time)

        # Spawn some canisters yo
        self.spawn_canister()

        if random.randint(1,100) == 100:
            pos = pygame.Rect((random.randint(20,680), random.randint(-10, 0)), (30,30))
            bounds = pygame.Rect((0,0), (self.size[0]-200,self.size[1]))

            s = EnemyShipBounce(pos, bounds, self.sprites, self.enemy_bullets, bounds.copy(), random.choice(EnemyShip.TYPE.keys()))
            s.active_weapon = Weapon(2500, CornersBulletTrajectory, 4, SmallBullet)
            s.active_weapon.set_sprite_group(self.enemy_bullets)

            x = random.random()
            y = random.random() * 2

            if random.random() > 0.5:
                x *= -1.0
            s.set_velocity(x,y)

        tospawn = self.level.progress_level(tick_time/self.level_advancement, 500)
        for instruct in tospawn:
            if instruct['type'] == 'BulletBurstBlue':
                sprite = BulletBurstBlue(pygame.Rect((instruct['x'],instruct['y']), (16,16)), pygame.Rect((0,0), self.size),
                                         self.enemy_bullets)
                sprite.set_layer(self.sprites, 11)

        if self.ship:
            # LOSE TEH GAMEZ?
            if self.ship.fuel <= 0:
                BulletHellGame.active_game.activate_screen('gameover')

                if BulletHellGame.active_game.score > 9000:
                    BulletHellGame.active_game.sounds.play_sound('sfx_cello/VictoryFF7CelloRip.ogg', volume=1.0)
                else:
                    BulletHellGame.active_game.sounds.play_sound('sfx_cello/Fail2.ogg', volume=1.0)
                return

            invincible = 'invincibility' in self.ship.powerups.keys()

            # Check Collisions
            shipcollisions = pygame.sprite.spritecollide(self.ship, self.sprites, False, pygame.sprite.collide_rect_ratio(0.7))
            shipcollisions += pygame.sprite.spritecollide(self.ship, self.enemy_bullets, False, pygame.sprite.collide_rect_ratio(0.5))

            for collider in shipcollisions:
                if collider == self.ship:
                    continue

                # Apply powerups
                if isinstance(collider, Canister):
                    BulletHellGame.active_game.sounds.play_sound('sfx/powerup1.wav', volume=0.5)
                    collider.score_sprite()
                    if collider.ctype == 'fuel':
                        if self.ship.fuel < 200:
                            self.ship.fuel += collider.score
                    else:
                        self.ship.add_powerup(collider.ctype)
                    self.remove_sprite(collider)
                # Ignore AttachmentSprite
                elif isinstance(collider, AttachmentSprite):
                    pass
                # Handle hitting bullets
                elif isinstance(collider, Bullet):
                    BulletHellGame.active_game.sounds.play_sound('sfx/explode1.wav', volume=0.9)
                    if not invincible:
                        self.ship.fuel -= collider.damage
                    collider.self_destruct()
                elif type(collider) == BulletBurstBlue:
                    BulletHellGame.active_game.sounds.play_sound('sfx/explode1.wav', volume=0.9)
                    if not invincible:
                        self.ship.fuel -= 10
                    collider.self_destruct()
                # Handle hitting enemies
                else:
                    BulletHellGame.active_game.sounds.play_sound('sfx/explode1.wav', volume=0.9)
                    if not invincible:
                        self.ship.fuel -= 10
                    collider.take_damage(10)

            # Process Enemies
            collisions = pygame.sprite.groupcollide(self.sprites, self.player_bullets, False, False, pygame.sprite.collide_rect_ratio(0.6))
            for collidee, colliders in collisions.items():
                # Only process enemy ships
                if isinstance(collidee, EnemyShip):
                    for collider in colliders:
                        collidee.take_damage(collider.damage)

                        if type(collider) == Missile:
                            BulletHellGame.active_game.sounds.play_sound('short-explode.wav', os.path.join('sounds', 'sfx'), 0.2)

                        collider.self_destruct()

        self.update_powerup_displays()

        # play some sound effects
        if [p for p in ['ammo','leftshot','backshot','rightshot'] if p in self.ship.powerups.keys()]:
            BulletHellGame.active_game.sounds.play_sound('sfx/shoot2.wav', volume=0.1)

        #Quick and dirty ship containment
        if self.ship:
            if self.ship.rect.x < 0:
                self.ship.rect.x = 0
            elif self.ship.rect.x > self.size[0]-200-self.ship.rect.width:
                self.ship.rect.x = self.size[0]-200-self.ship.rect.width

            if self.ship.rect.y < 0:
                self.ship.rect.y = 0
            elif self.ship.rect.y > self.size[1]-self.ship.rect.height:
                self.ship.rect.y = self.size[1]-self.ship.rect.height

    def remove_sprite(self, sprite, groups=None):
        if not groups:
            groups = [self.sprites]
        elif not isinstance(groups, (tuple, list)):
            groups = [groups]

        for group in groups:
            group.remove(sprite)

    def remove_display(self, string):
        self.remove_sprite(self.get_display(string))

    def update_powerup_displays(self):
        displays = []

        for powerup in self.ship.powerups:
            display = self.get_display(powerup)

            if not display and powerup != 'fuel':
                display = PowerupDisplay(pygame.Rect((525, 65), (50, 15)), self.displays, powerup)

            if display:
                displays.append(display)

        yoffset = 65

        for display in displays:
            display.rect = pygame.Rect((525, yoffset), (50, 15))
            yoffset += 20

    def get_display(self, string):
        for display in self.displays:
            if display.string == string:
                return display
        return None

    def spawn_canister(self):
        if random.randint(1,100) != 100:
            return

        # determine what types of canister to spawn
        very_common = ['fuel']
        common = ['ammo', 'buckshot', 'backshot', 'leftshot', 'rightshot']
        rare = ['invincibility', 'missiles', 'flamethrower', 'random']
        very_rare = ['nuke']

        d100 = random.randint(1,100)

        if d100 <= 50:
            ctype = random.choice(very_common)
        elif d100 <= 80:
            ctype = random.choice(common)
        elif d100 <= 95:
            ctype = random.choice(rare)
        else:
            ctype = random.choice(very_rare)

        sprite = Canister(pygame.Rect((random.randint(10, 480), 0), (20,20)), pygame.Rect((0,0), self.size),
                          self.sprites, ctype)
        sprite.set_layer(self.sprites, 9)

        x = random.random() * random.choice([-1,1])
        y = random.random() * 2

        sprite.set_velocity(x,y)

    # BOOM
    def detonate(self):
        BulletHellGame.active_game.sounds.play_sound('sfx/nuke1.wav', volume=0.2)

        self.player_bullets.empty()
        self.enemy_bullets.empty()

        for sprite in self.sprites:
            if not isinstance(sprite, (UserShip, AttachmentSprite)):
                sprite.score_sprite()
                sprite.self_destruct()
