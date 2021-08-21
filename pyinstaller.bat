REM Edit paths before running:
C:\python27\python "E:\Program Files\pyinstaller-pyinstaller-337ae69\pyinstaller.py" -w -F main.py enemy_sprites.py bhgame.py gameovermenu.py keyed_config_controller.py keypath_store.py levels.py mainmenu.py rail_level.py ship.py bhsprite.py user_sprites.py velocity_controller.py weapon_system.py  ldpygame\__init__.py ldpygame\asset_manager.py ldpygame\clock.py ldpygame\event_responder.py ldpygame\game.py ldpygame\menu.py ldpygame\screen.py ldpygame\sprite.py ldpygame\sprite_events.py ldpygame\timer.py

pause
REM If packaged as single file.
xcopy /s /I fonts dist\fonts
xcopy /s /I images dist\images
xcopy /s /I sounds dist\sounds
xcopy /s /I levels dist\levels
REM xcopy /s /I fonts dist\main\fonts If packaged as directory
REM xcopy /s /I graphics dist\main\images
REM xcopy /s /I sounds dist\main\sounds
pause

