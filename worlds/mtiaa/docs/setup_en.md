# My Teacher Is an Alien Archipelago Setup Guide

## Requirements

* *My Teacher Is an Alien* game files from your own copy of the game
* DxWnd and the MTIAA configuration file
* MTIAA-Installer.zip file
* MTIAA APWorld (`mtiaa.apworld`)

## Installing the Game Patch

1. Copy the entire contents of your *My Teacher Is an Alien* game disc or ISO to a folder on your computer.

   * **NOTE:** MTIAA has some limitations on where the game can be located. Keep the full path to at most 119 ASCII characters long.
2. Extract `MTIAA-Installer.zip`. Where it is extracted to doesn't matter.

   * **NOTE:** Do not extract the `MTIAA-AP-TEACHER.patch.zip` file. Leave that intact.
3. Double-click `INSTALL_MTIAA_AP.cmd`.
4. When prompted, paste the path to the folder that contains your original `TEACHER.EXE` and `DATA` folder (usually the folder labeled `CDDATA`) and press Enter.
5. Wait for `SUCCESS` to appear. This will preserve your original executable file as `TEACHER.ORIGINAL.EXE` and patch the AP version to `TEACHER.EXE`.

## Installing DxWnd

1. Download and unpack/install the latest build of DxWnd: https://sourceforge.net/projects/dxwnd/files/latest/download
2. Download the DxWnd configuration file for MTIAA from this GitHub release.
3. Open DxWnd, select **File > Import...**, and select the MTIAA configuration file.
4. Right-click the new entry for *My Teacher Is an Alien*, click **Modify**, and under the **Main** tab, update the Path to point to the patched `TEACHER.EXE` file.
5. Optional: You can perform the following settings changes as you wish:

   * Under **Modify > Main**, you can adjust the W and H values to the window size of your preference. 1280 x 960 will provide a 2x scaling.
   * Under the **Mouse** tab, changing Mouse Clipper from ON to Default will allow the mouse to move outside the window.
   * If you click outside of the game window, the game will freeze in the background. Under **Main > Generic > Do not notify on task switch**, this will keep the game running in the background.

## Playing the Game

1. If you haven't already, install the `mtiaa.apworld` file by opening the Archipelago Launcher, selecting **Install APWorld**, and selecting `mtiaa.apworld`.
2. Open **My Teacher Is an Alien Client** from the Archipelago Launcher and connect to your room.
3. Launch the game through DxWnd and choose **New Game** once the client is connected.
4. You can save and quit to return to your previous progress as needed.

   * **NOTE:** Save files can be named. It is recommended to name saves as needed based on your player name. Loading the wrong save can affect inventory, character availability, and period progression.
5. If you are playing multiple seeds of MTIAA, you must close the game when you switch between them. You do not need to close/reopen the client. Close the game, disconnect and reconnect the client to the new seed, and then reopen the game.

If you have Universal Tracker installed, a **Tracker** tab will also appear in the client, displaying logically available checks.

## Installer Troubleshooting

* **Installer says it cannot find `TEACHER.EXE` or `DATA`:** Make sure that you have selected the folder that has both files (usually the `CDDATA` folder).
* **No checks or items are appearing:** Make sure you are connected to the client before opening the game and that you have opened the patched exe file, not the original exe file.

## In-Game Troubleshooting

* **I received a Progressive Period, but it restarted the period:** If you received a Progressive Period at the very end of a period, it will restart the previous period. Quickly move through the period again and it will continue the game.
* **My only available character(s) are either in Detention or Suspended and I cannot continue:** That is intended behavior. This game supports restarting and reloading saves. If you only have one character and they get detention, you may have to reload a previous save or start a new game.
* **I cleared two of the teachers but that meant the third teacher was the alien. How do I clear them?:** You will need to start a new game in order to perform the other tests. Save your original game before you start a new game, perform the tests you need, then return to your save file.
* **I already determined the alien but still need to perform tests:** You will need to start a new game in order to perform the other tests. Save your original game before you start a new game, perform the tests you need, then return to your save file.
* **Why did I get a Game Over after completing Monday - Period 4?:** You will receive a Game Over at that point if you have not learned about students being kidnapped. Talk to Linsey or Mike, witness Mike getting kidnapped, or speak with the other playable characters during lunch or at the library to learn about the kidnappings.
* **Why did I get a Game Over after completing Wednesday - Period 2?:** You will receive a Game Over at that point if you have not identified the alien yet.
* **Why did I get a Game Over after completing Thursday - Period 1?:** You will receive a Game Over at that point if you have not rescued at least one student from the aliens. You can either shoot the orbs as they are kidnapping a student or board the spaceship and rescue them from one of the rooms on the ship.
