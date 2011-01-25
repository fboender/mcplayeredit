
MCPlayerEdit  v0.7

About
-----

MCPlayerEdit is a Minecraft player- and inventory editor.

Features include:

- Modifying the inventory.
- Adding kits (collections of items) to the inventory.
- Showing and moving the player and spawn point coordinates.
- Setting the in-game time of day.
- Bookmark locations and warp back to them (works inter-dimensional).
- Track your inventory in case of death.
- Commandline history
- Commandline tab-completion (only on GNU/Linux, WinXP for now)

!! WARNING !!

  This software may corrupt your Minecraft save file(s), and sneak up on you
  when you least expect it and go SSSSSSssss BOOOM. You have been warned, make
  backups!

  A backup of the level.dat file is automatically created when you make
  changes. You can find it in your Minecraft Save game folder under the name
  'level.dat.bak'. In case of emergency, scream, cry, rename 'level.dat.bak' to
  'level.dat' and things should be alright again.

Requirements
------------

* Python 2.6+
* readline (libreadline) for tab-completion support.

Compatibly
-----------

Developed for and on:

    Ubuntu 10.04 / Python 2.6.5

Confirmed to be working on:

	- Ubuntu 10.04
	- Windows XP (Limited tab-completion functionality)
	- Windows 7 (Limited tab-completion functionality)
	- Mac OS X 10.5.5

Should work on:

    - Every Unix-like OS
    - MacOSX
	- Windows Vista

Usage
-----

GNU/Linux, Unix-compatible:

	Unpack the tarball

    $ tar -vxzf mcplayeredit-0.1.tar.gz

	Start MCPlayerEdit

    $ cd mcplayeredit
    $ python ./mcplayeredit
    > load <worldnr>

Windows (XP, 7):

    - Unpack mcplayeredit-0.1.tar.gz with something like 7zip.
    - Navigate to the mcplayeredit folder
    - Double click the 'mcplayeredit.py' file.

MacOS X:

	Using Finder

    - Download mcplayeredit-0.5.tar.gz 
	- Open the containing folder
	- Double-click the .tar.gz file to extract it.
	- Open the extracted mcplayeredit-0.5 folder
	- Double-click the 'mcplayeredit.py' file. This will most likely open it in
	  the Python IDLE editor
	- Press F5 to run the Python script.

Make sure you are not playing the World in Minecraft before loading the level
in MCPlayerEdit, or your changes will not take effect. You can modify a world
with Minecraft closed, waiting on the main screen or when playing another
World.

You do not have to close MCPlayerEdit after editing a world, but if you have
played the world in Minecraft, please issue a `reload` before making any
changes.

Some usage examples:

	(You can use tab completion if your on Linux. Tab completion also works on
	Win XP/7, but is not as full-featured as on *Nix systems)

    > load 1
    Loaded.

    World 1> move spawn
    Moved spawnpoint to current player position

    World 1> list
    slot   0 ( quick inventory):  1 x Bow
    slot   1 ( quick inventory):  1 x Iron Sword
    ...

    World 1> items tn
       46: TNT

    World 1> give 64 tnt
    Added 64 x TNT in slot 0

    World 1> items diamond
      264: Diamond
      279: Diamond Axe
       57: Diamond Block
      313: Diamond Boots
      311: Diamond Chestplate
      310: Diamond Helmet
      293: Diamond Hoe
       56: Diamond Ore
      312: Diamond Pants
      278: Diamond Pickaxe
      277: Diamond Spade
      276: Diamond Sword

    World 1> give 1 diamond pickaxe
    Added 1 x Diamond Pickaxe in slot 1

    World 1> give 64 264
    Added 64 x Diamond in slot 3

    World 1> bookmark Pit of DOOM
    Bookmark 'Pit of DOOM' created.

    World 1> warp
    The following bookmarks have been set:
      Isle of Despair: 343.079559 61.620000 -198.879712
      Pit of DOOM: 341.527171 73.620000 -233.944163

    World 1> warp Isle of Despair
    Warped player position to Isle of Despair

    World 1> save
    Saved. Backup created (/home/user/.minecraft/saves/World1/level.dat.bak)
   
    World 1> exit

Copyright
---------

MCPlayerEdit Copyright(R) by Ferry Boender.

Released under the MIT license.

This program uses a modified version of the NBT library from pymclevel by
Codewarrior0. The full library can be found at
http://github.com/codewarrior0/pymclevel and is licensed under the MIT license.

Credits:

 Libs

   CodeWarrior0 for the excellent NBT Python lib (I hacked it a bit)

 Contributions / Testing

    Camel            (suggestions)
    LadyCygna        (testing, suggestions)
	Lillefix         (documentation fix)
    Maramonster      (testing, suggestions)
    Yobbobandana     (bugfixes, patches)
	Foone            (warpto command patch)
	Dustin Pyle      (kitsave patch)
	Stephen Rollyson (bugfixes, patches)

Development
-----------

Send bugs, feature requests, patches and beer to:

  ferry.boender AT gmail.com

Or:

  ferry.boender AT electricmonk.nl

Subversion repository is here:

  https://svn.electricmonk.nl/svn/mcplayeredit/trunk/
  
Please provide patches in Unified Diff format:

  diff -Naur OLDFILE NEWFILE > mcplayeredit-DESCRIPTION.patch

In case the patch gets accepted, I will credit you in the revision logs,
HISTORY.txt and README.txt with the name from your email (I will not include
the email address). If you do not want this, or want to be credited under
another name, please let me know!

