# FICO® Xpress Optimization

# Xpress Installation Guide


#### Release 9.9


#### __Last update 20 August, 2026__



(C) 2013-2026 Fair Isaac Corporation. All rights reserved. 
This documentation is the property of Fair Isaac Corporation ("FICO"). Receipt or possession of this documentation does not convey rights to disclose, reproduce, make derivative works, use, or allow others to use it except solely for internal evaluation purposes to determine whether to purchase a license to the software described in this documentation, or as otherwise set forth in a written software license agreement between you and FICO (or a FICO affiliate).  Use of this documentation and the software described in it must conform strictly to the foregoing permitted uses, and no other use is permitted.

The information in this documentation is subject to change without notice. If you find any problems in this documentation, please report them to us in writing. Neither FICO nor its affiliates warrant that this documentation is error-free, nor are there any other warranties with respect to the documentation except as may be provided in the license agreement. FICO and its affiliates specifically disclaim any warranties, express or implied, including, but not limited to, non-infringement, merchantability and fitness for a particular purpose. Portions of this documentation and the software described in it may contain copyright of various authors and may be licensed under certain third-party licenses identified in the software, documentation, or both.

In no event shall FICO or its affiliates be liable to any person for direct, indirect, special, incidental, or consequential damages, including lost profits, arising out of the use of this documentation or the software described in it, even if FICO or its affiliates have been advised of the possibility of such damage. FICO and its affiliates have no obligation to provide maintenance, support, updates, enhancements, or modifications except as required to licensed users under a license agreement.

FICO is a registered trademark of Fair Isaac Corporation in the United States and may be a registered trademark of Fair Isaac Corporation in other countries. Other product and company names herein may be trademarks of their respective owners.

Patent(s): [www.fico.com/en/patents](https://www.fico.com/en/patents})

FICO® Xpress Optimization 9.9

Deliverable Version: A

Last Revised: 20 August, 2026


## Chapter 1 FICO Xpress Installation


### Section 1.1 Introduction


This document describes how to install the FICO Xpress Optimization Suite for using the software in several operating systems.

For installation instructions pertaining toFICO® Xpress Insight, please see the Xpress Insight Installation guide.

If you have any problems with your Xpress license, please refer to Chapter  _FICO Xpress Licensing_. This Chapter also tells you what information you must supply to FICO Support if you cannot resolve the problem on your own.

### Section 1.2 Downloading the Installation Packages


To install Xpress, use the installer packages available from the downloads area of the FICO Xpress website. When downloading a new release, make sure that you pick the correct installer for your system and license. For example, if you want to use a Linux 64-bit Xpress on an Intel platform, make sure this is the package you download \(and not, for example, Linux 64-bit for ARM\).

There are three types of installer;

 * an _InstallShield_ Windows version
 * an install script version for all the Linux and Unix installers, and
 * a DMG file for macOS.

To install an Xpress patch rather than a full Xpress installation, see the section  _Patch Installation_.

### Section 1.3 Installing Xpress on Microsoft Windows


Use the Microsoft Windows _InstallShield_ installers, which are self-extracting executable files downloaded from the FICO Xpress website.

#### Installation Prerequisites for Windows Installation


There are no prerequisites for Windows installations.

 1. To install the software, double-click the left mouse button on the file you downloaded.
 2. Once the files have been extracted from the package, the _InstallShield_ installer displays the following window:

![install2.png](Graphic/install2.png)



 3. Click **Next**  to continue with the installation.

 4. Next you will be presented with the Xpress licensing agreement as shown below:

![install3.png](Graphic/install3.png)


   *  It is important that you read this agreement and make sure that you agree to its terms and conditions. Use the scroll bar \(highlighted in green\) to read the complete agreement. Click **Print** to print the agreement text.

 5. Click **Yes**  if you agree with the terms. \(If you click **No** , the installer will automatically close.\)

 6. Accept the default installation location \(or navigate to the desired location\) then select what type of installation you wish to have:

![install3b.png](Graphic/install3b.png)



 * The **Typical**  install, where the most commonly-used components \(but not all\) will be installed
 * The **Custom**  install, where the user can pick and choose.
Those wishing to install Xpress Kalis support or drivers for dongle licensing keys will need to select the 'Custom' option. The default Custom install options are:

![install3c.png](Graphic/install3c.png)


   *  If you request the Kalis Solver, you will be required to agree to a separate Kalis End-User License Agreement before you can proceed.

 7. Selection of the license type:

![install4.png](Graphic/install4.png)


 * **Community License** : Choose this to use the software with the free FICO Xpress Community License for academic and commercial use. The capacity limitations previously listed in  _For Community License_ apply. The software will install for the local machine only.
 * **Static Licensing** : Choose this to use the software with a **paid**  or **evaluation**  license. The software will install for the local machine only. Click **Next** . Note that if you select the Static licensing option and plan on using a dongle to license Xpress, you will be able to move the dongle between machines, but only one machine at a time can access the software.
 * **Floating Licensing** : Choose this to use the software with a **paid**  license. The software will install for the current network. Click **Next** .
 * **License Server** : Choose this to setup a server so other users can use floating client licenses.
Note that if you already have a license file in place, the simplest thing to do is just leave it at the default of a Static license and continue with the installation.

### Section 1.4 Post Installation Tasks \(For Static or Floating Server License\)


After the software has installed, you will be prompted to point to the license file and the environment variables will be set. This is not needed if the license file is already in place in  _e.g._  `c:\xpressmp\bin`

 



![install10.png](Graphic/install10.png)






 * _If you have a license file from FICO Support_, click **Browse**  and enter the folder in which the license file \( `xpauth.xpr`\) is located. Click **Next** .
 * _If you do not have a license file from FICO Support,_ you can continue; however the license file created in the Xpress installation directory will not be a valid file, just a temporary placeholder until you have a valid license.
 * _If you are installing a License Server_, you will be asked if you wish to install this as a Windows Service. If not, you will have to start/stop the Server manually, via the `xpserver.exe` executable.

#### For Community License


The Community License file bundled with Xpress will be copied in place to serve as your license.

#### For Client Floating License


You will be prompted to provide the details of the License Server:

![install7a.png](Graphic/install7a.png)




Enter the hostname or IP address, and a client license file will be written that targets the given server.

#### Subsequent changes to the installation


If you re-run the installer while Xpress is still installed, you will be given the option to **Modify**  your installation by adding and/or removing components. Note that in this case, the license handling referred to above will not take place: any required licensing changes can be performed manually. See  _Manual Installation_ for details.

### Section 1.5 Advanced Windows Installer Options


The FICO® Xpress software can be installed and removed interactively using the Windows operating system user interface. There is also the option to automate these processes.

#### Command Prompt Options


There are two tiers of options: the first set are used by the installer, the second are forwarded by the installer to the built-in Windows application `msiexec.exe` which handles the bulk of the installation process.

##### Available Options When Using the Installer



__Option__ | __Description__ | 
---------- |  ---------- | 
/? | Show all the available options | 
/x | Uninstall the application | 
/s | Suppress the initial UI \(for more, see Section _Silent Installations_below\) | 

##### Available Options When Using `msiexec.exe`



__Option__ | __Description__ | 
---------- |  ---------- | 
"/v /?" | Show all the available options | 
"/v /quiet" | Silent installation \(for more, see Section _Silent Installations_below\) | 
"/v /L\\" _path_to_logfile_\\" " | Default logging | 
"/v /Log\\" _path_to_logfile_\\" " | More detailed logging | 
"/v INSTALLDIR=\\" _path_to_install_dir_\\" " | Override installation directory | 
"/v ADDLOCAL= _Features_" | Select which features to add \(see below\) | 
"/v REMOVE= _Features_" | Select which features to remove | 

While the various "/v" options can be used separately, and are documented this way in the previous tables, it is best practice to combine them into a single quoted section. For example, a silent install which has detailed logging and an overridden installation location could have the following options \(the AGREE\_XPRESS\_EULA=1 will be explained in a later section\):

```
/s "/v /quiet /Log \"logfile.txt\" INSTALLDIR=\"c:\MyXpressmp\" AGREE_XPRESS_EULA=1"
```


**Notes:** 

 * You do not need to specify an INSTALLDIR; `c:\xpressmp` will be used by default.
 * There are many other options available to both the installer and `msiexec.exe`. Only use the recommended options listed above. Care should be taken when using any other options.
 * Backslashes are only required before a quote; a sequence of backslashes are required immediately before a quote, inside a quoted section. The command- line is split into tokens, when using backslashes and quotes. For more, see the documentation for the Windows API function `CommandLineToArgvW`.
 * Given the complexity of nested arguments, be aware of your shell or scripting language's rules on variable interpolation, escaping _etc._  to avoid producing a malformed command-line.
 * As with the installer UI, the destination for the application code can only be set \(via INSTALLDIR\) on original installation; in-place modifications will act on the current installation location.
 * On a command-prompt or Windows batch file, the system will not wait for the installer to finish before continuing. To force it to wait in a batch file, place the `call` directive at the very start of the command-line \(before the path to the installer\). In this case, the `if errorlevel` conditional logic and the `% errorlevel%` pseudo-environment variable can be used with the return code of the installer in the usual manner. Note that the return code might be negative in case of failure.
   *  Another option is to prefix the command with `start /wait "" ...`where the empty string is needed prior to the path to the installer. If run in a Windows shell, this will cause the shell to wait for completion, and the result can be inspected via `% errorlevel%`as mentioned above.

#### Silent Installations


Many of the options here are substitutes for actions that can be done via the installer UI that means they can be specified in a script and run without user intervention.

When using this option, it is worth taking a log, using the "/v /L" or "/v /Log" options mentioned in _Available Options When Using msiexec.exe_ in the previous section  _Command Prompt Options_, in case any problems are encountered. The installer detects that the procedure is intended to be silent and will not show any error message dialogs.

**Note:**  Logging directives are omitted for space and clarity in the following section. You should specify a log file when performing silent installation operations.

Two or three directives are needed for a truly silent installation:


__Directive__ | __Description__ | 
---------- |  ---------- | 
/s | Installer option will hide the opening dialogs as the installer is being unpacked before running | 
"/v /quiet" | `msiexec`option suppresses the UI for the rest of the installation | 
"/v AGREE\_XPRESS\_EULA=1" | Signifiy that you have read and agree to the Xpress End-User License Agreement \(only needed on original installation, not on further modifications or uninstall\) | 

To perform the equivalent of a Custom install silently, use the ADDLOCAL option defined earlier to set which parts of Xpress are included. The options are:

 * **ALL**  for every optional component
 * **Xpress**  for the for the core Xpress installation
 * **Workbench**  for the Xpress Workbench IDE \(this is included by default\)
 * **Kalis**  for the Xpress Kalis solver \(this is _not_ included by default\)
 * If installing the Xpress Kalis solver, either explicitly via `Kalis` in ADDLOCAL or implicitly via `ALL`, you need to read and agree to the Kalis End-User License Agreement, and include the `AGREE_KALIS_EULA=1` property on the command-line in the "/v ..." quoted section

 * **Dongles**  for USB dongle driver to support hardware license keys \(this is _not_ included by default\)

The case of letters is significant.

If ADDLOCAL is not specified, the Xpress and Workbench components will be installed. If you wish to just install the bare minimum, specify ADDLOCAL=Xpress.

**Note:**  Multiple elements for the ADDLOCAL or REMOVE value can be listed sequentially separated by commas. For example, "/v ADDLOCAL=Xpress,Kalis"

#### License Handling


The default behaviour is to act on the `xpauth.xpr` file already in the Xpress `bin` folder. If you wish to customize license handling, you can set some properties in the "/v ..." section:

 * **LIC_TYPE** : can be `COMMUNITY`, `STATIC`, `CLIENT` or `SERVER`
 * **LIC_SERVER_HOST** : if `LIC_TYPE` is `CLIENT`, the hostname or IP address of the License Server to use in creating the Client License. Defaults to `localhost`.
 * **LIC_SERVER_AS_SERVICE** : \(1 or 0\) if `LIC_TYPE` is `SERVER`, whether to install the License Server as a Windows Service. Default to `0`.

Note that the post-install license handling performed in the UI for Server and Static licensing has no equivalent behaviour in a silent installation. The recommended course of action in this case is to put the `xpauth.xpr` file in place in the Xpress `bin` folder prior to installation.

#### Silently Modifying an Existing Installation


You can modify or remove an installed instance of Xpress by running the installer in the usual interactive way.

The equivalent silent operation will not modify what elements are included unless ADDLOCAL or REMOVE are used, in which case the elements will be added or removed as directed.

No error is generated if you add an element that is already present, or remove one that is already absent; no action is taken in either case.

As in new installations, ADDLOCAL can use the special value `ALL` to ensure that all elements \(except those optionally specified by REMOVE\) are installed. Silent installations and silent modifications are invoked in the same way.

You do not need to include the `AGREE_XPRESS_EULA=1` property on modification of an existing installation, and you only need the `AGREE_KALIS_EULA=1` property if you are adding the Kalis component.

License setup is only done on initial install. After that, you can change licensing by updating the `xpauth.xpr` file directly.

#### Silent Uninstallation


To uninstall silently, use the following options:

```
/x /s "/v /quiet"
```


### Section 1.6 Installation on Linux or Unix


To install Xpress on Linux and Unix variants, use the install script contained within the downloaded tar archive file. You must untar the required files from the downloaded file. As such, it is recommended that you not perform this task from your base directory.

#### Prerequisites for Linux Installations


_**Note:**  If you have an Xpress license, it is recommended that you make a note of the full directory path that contains the file \( `xpauth.xpr`\) before you begin installation since you will need this information._

 1. To extract the files from the tar archive and start the installation script, enter the following commands. \(For this example the installation is for an 9.6 Linux 64-bit version; as such, your tar file may have a slightly different name depending on the Xpress version and system on which you are installing.\)
```
tar xf xp9.6.0_linux_x86_64_setup.tar
cd xp9.6.0_linux_x86_64_setup/
./install.sh
```

 After script start up, you will be prompted to answer a series of questions to set up the installation. \(You can exit the installation process at any time by pressing the _Ctrl_ and _c_ keys at the same time.\)

 2. First, the license agreement is displayed. This can be scrolled through quickly using the Space bar key, or scrolled through slowly using the up and down arrow keys or _Enter_. Pressing **q**  stops the display of the licensing agreement, at which point you will be asked if you agree to its terms. Press **n**  or **y** . If you don't accept the license, the installer will exit.

 3. Specify the type of licensing you wish to use: choose from community \(free FICO Xpress Community License for academic and commercial use; the capacity limitations previously listed in  _For Community License_ apply\), static \(one computer, or a dongle for a non-server installation\), floating, or web-floating. Also note the following when responding to the prompts:
     * In this and all of the other installation questions, valid options are visible in the question text surrounded by square brackets. For example, at this point there are four options:\( c\) ommunity,\( s\) tatic,\( f\) loating, or\( w\) eb-floating. Therefore valid entries are **c**  or **s**  or **f**  or **w** .
     * When the question requires a yes/no answer, you must type **y**  or **n** .
     * When entering a directory path, type the full path, or press _Enter_ to accept the offered default path.


 4. _If you opted to install a floating license,_ you will be prompted to indicate whether you want a\( s\) erver or a\( c\) lient installation. If you will be connecting to another computer \(or another XPserver Xpress license manager on the same machine\) then enter **c** ; if you want to make this machine the license server then enter **s** .

 5. _If you opted to install a web-floating license_, see  _Using Key-based (Static or Web Floating) Licenses_ for more information.

 6. Determine where to install the software: The default is `/opt/xpressmp`. Press _Enter_ to accept the default. To install to a different location, enter the full path, making sure to use forward slashes `"/"`. You may enter the relative path if you wish, but this may affect how the environment variables are set later in the installation process. The supported method is to enter the full path.

 7. You will be prompted to select which components you wish to install. Answer **y**  or **n** . Default is to install the FICO Xpress Mosel, FICO Xpress commandline interface, FICO Xpress Optimizer interfaces, FICO Xpress developer libraries and headers, and Examples components. FICO Xpress Kalis is not selected to be installed by default.

 8. Using the Xpress Kalis constraint programming engine: this is an optional component for use in the Mosel modeling environment. It requires the relevant licensing option in order to authorize its use; however, anyone can install the add-on provided they accept the terms and conditions.
 
If you select to install the Kalis component, the Kalis licensing agreement is displayed. Controls are the same as above. Press **n** or **y** to reject or accept. If you don't agree to the license, the installation of the Kalis components will be skipped.

 9. Add Xpress installation paths to your .bashrc file: by doing this, Xpress command-line tools can be accessed from any Bourne shell \(bash\) you create. If not, you will have to manually source the `xpvars.sh` file to use Xpress tools. Press **n**  or **y** .

 10. License file: you will be prompted to indicate whether you have an Xpress license file from FICO Support.
     * _If you do not have a license,_ enter **n** . At this point, you can stop the installation in order to obtain the license file from FICO Support and then perform the installation once you have it. Or you can continue with the installation and get the license file at a later date. If you choose the latter option, you will need to place the license file in the `bin` directory of your Xpress installation. For instance, in the preceding example, \( `/opt/xpressmp`\) you would copy the `xpauth.xpr` license file in to the `/opt/xpressmp/bin` directory.
     * _If you indicated earlier that you have an Xpress license and provided its location,_ you will be prompted whether you want to copy the license file to the default directory \(which is `/opt/xpressmp/bin` for this example\). This is the default option.
     * _If you decide not to use the default location for the Xpress license,_ Xpress will still work correctly; however you should make a careful note of where the license file is stored in case it requires updating at a later date.
     * Once installation is complete, the location you have set for the license file will be stored in the `XPAUTH_PATH` environment variable.
 The files will now be extracted from the tar archive. Depending on the speed of the computer, this may take only a few seconds or it may take as long as a few minutes.

 11. _If you indicated earlier that you were installing a floating client,_ you will now be prompted for the name of your license server. If you know the name, enter it now. If you do not know the server name, press _Enter_ and make a note of the onscreen instructions for entering the server name at a later date. \(You can alter the server name in the `xpauth.xpr` license file using any text editor, such as Emacs or Vi.\)

 12. On completion, the installer generates two script files, one for the Bourne shell \( `xpvars.sh`\) and another for the C shell \( `xpvars.csh`\). These scripts should be run, as detailed in the installer output, to set up the shell environment so that Xpress runs correctly. Add them to any user profiles or service startup scripts that will be making use of Xpress.

 13. If you need to set any custom environment variables for Xpress \(in the Bourne shell\) you can create a file called `xpvars.local.sh` alongside the generated `xpvars.sh` file and export custom environment variables from this script.

 14. _If you did not have your license file while performing the installation,_ you will need to set the `XPAUTH_PATH` environment variable to point to it once you do have it. The instructions for doing this from the command line are described within the installer output.

 15. _If you want to add the change to `XPAUTH_PATH` to a more permanent script that can be run whenever the shell is opened,_ then the best option would be to edit the relevant `xpvars` script in the `bin` directory of your Xpress installation. You can edit these files with any Linux/Unix text editor by altering the line relating to the `XPAUTH_PATH` environment variable \(since this is the location of the license file\).

 16. _If you indicated earlier that you were installing a floating server installation,_ the install script attempts to start the XPserver license manager.

 17. _If you do not have a server license,_ then an error message is displayed. If it starts successfully, then any log messages from it will be output in to the `xpress.log` file. By default the `xpress.log` file is written to `/var/tmp/xpress.log`. For more information, see [FICO Xpress Licensing](#chapinst2).

 20. The Optimizer solver console has a dependency on `libncurses.so.6` on Linux platforms. This library may not be installed by default in your Linux distribution. If you need to use the Optimizer console program, you may need to install `libncurses` 6 using your package manager.

Once the environment variables have been set using the script and a valid license file is present, then the Xpress software is ready to use.

_**Note:**  Previous releases of Xpress used the `XPRESS` environment variable to locate the license file. This is now deprecated in favour of the `XPAUTH_PATH` environment variable. When upgrading, please update any existing user scripts which set `XPRESS` so that they instead set `XPAUTH_PATH`._

#### Automated installation on Linux or Unix


As well as the guided installation detailed in the previous section you can also use the Xpress installation script as an automated installer by providing command-line options.

To get a list of the available options run:

```
./install.sh -h
```


You can specify as many options as you like, if there are any required options missing you will be prompted for these with interactive prompts. If you require the installation to be fully automated make sure you supply all the necessary options so that the interactive prompts do not appear.
 `--no-interactive`
By passing the `--accept-xpress-license` or `--accept-kalis-license`, you agree to their terms and conditions respectively.

Here is an example of a fully automated installation assuming you are in a directory containing the Xpress tar archive and a valid `xpauth.xpr` license file:

```
mkdir xp960
tar xf xp9.6.0_linux_x86_64_setup.tar -C xp960/
pushd xp960/xp9.6.0_linux_x86_64_setup/
./install.sh --no-interactive --license-type static --components full --install-path \
~/tmp2/xpressmp --xpauth-path ../.. --accept-xpress-license --accept-kalis-license
popd
```


### Section 1.7 Installation on macOS


The macOS application is downloaded in a DMG file.

 1. If you have Xpress installed, back up any existing Xpress licence file, then open the **Applications**  folder. Right click on the FICO Xpress folder and select **Move to Trash**  to uninstall.
 2. Double-click the downloaded DMG file to display the license agreement.
 3. Click **Agree**  to continue the installation. A Finder window is displayed, showing the application and a shortcut to your **Applications**  folder.
 4. Drag the **FICO Xpress**  icon to your **Applications**  folder to install the application.

 * The FICO Xpress folder includes a copy of **Xpress Workbench**  that provides direct support for the authoring, editing, executing and debugging of Xpress Mosel models and FICO Xpress Solutions. You can create a shortcut to the **Xpress Workbench**  application by opening the **Applications > FICO Xpress**  folder and dragging the Workbench icon to the Dock.
 6. Optionally, copy the **FICO Xpress Examples**  folder, that contains a range of useful resources including code examples, to your preferred location and unzip it.
 7. When the installation is complete, unmount the DMG file. Ctrl-click in the Finder window and select **Eject "FICO Xpress Installer"** . You can then delete the DMG file
 8. Finally, create a new folder in `<HOME>/Documents/` named `FICO Xpress Config` and copy the license file to it.

#### Environment variables


To use the command-line tools, certain environment variables need updating. At a console or in a shell script, enter

```
. /Applications/FICO\ Xpress/xpressmp/bin/xpvars.sh
```


and the variables will be set.

_**Note:**  The backslash \(\\\) between "FICO" and "Xpress" is needed to escape the space character. If you use quoting and auto-completion at the macOS console by pressing TAB, the closing slash will be added outside the quotes and TAB-completing further will automatically undo the quoting. This means;_

```
. "/Applications/FICO
```


_will autocomplete to;_

```
. "/Applications/FICO Xpress"/
```


_Therefore, use backslash escape instead._

```
. /Applications/FICO\ Xpress/xpressmp
```


### Section 1.8 Manual Installation


In the unlikely event that the provided installers fail to function correctly, the software can be extracted manually.

Unix and Linux variants should by default contain the necessary programs to unzip and extract from the tar archives. If you do not have an extraction program, you will need to install one. If this is the case and your previous attempt at automatic installation using the install script failed, then the lack of an extraction program may be the cause. In this case, install the required tools and attempt an automatic installation again.

The differences between the automatic and manual installation methods are as follows:

 * Files are not installed selectively as the whole archive will be uncompressed.
 * Not all environment variables are automatically set.
 * The XPserver license manager will not be automatically configured to run as a service.

_**Note:**  When performing a manual installation, you must manually set the required environment variables for your platform. See Section  _Environment Variables Reference_ for a complete list of environment variables and their descriptions._

#### Manual Linux/Unix Installation


As mentioned previously, if the installation fails, it is likely that there was a problem using the standard zip and tar programs. If this is not the case, then you can manually install the software by following these steps:

 1. If you have not done so, untar the downloaded installer \(if you have attempted to install via the automated install script then you have already performed this step\). This command extracts the files from the tar archive:
```
tar xf name_of_downloaded_installer.tar
```



 2. The extracted files include the installation script `install.sh`. Move the `.gz` file to the directory where you want to install the software.
   *  Decompress the `.gz`file using the following command:
```
gunzip name_of_gz_file.gz
```



 3. The preceding command extracts another tar archive which itself contains the installation files and may be unarchived using the following:
```
tar xf name_of_new_tar_file.tar
```



 4. The installation directory should now contain several directories of files and several license and html files. Read the license files and make sure you agree with the terms and conditions; if you do not agree to them, delete the software and discontinue the installation.

 5. Copy your `xpauth.xpr`  license file to the `bin` directory of the Xpress installation. If you are working with a Community License, rename or copy the provided file `community-xpauth.xpr` to `xpauth.xpr`.

 6. Set the relevant environment variables so that your system can find the Xpress executables, runtime libraries and license file. For example, on a Linux system using the C shell:
```
setenv XPRESSDIR your_xpress_install_directory
setenv PATH $XPRESSDIR/bin:$PATH
setenv LD_LIBRARY_PATH $XPRESSDIR/lib:$LD_LIBRARY_PATH
setenv CLASSPATH $XPRESSDIR/lib/xprs.jar:$CLASSPATH
setenv CLASSPATH $XPRESSDIR/lib/xprb.jar:$CLASSPATH
setenv CLASSPATH $XPRESSDIR/lib/xprm.jar:$CLASSPATH
setenv XPAUTH_PATH $XPRESSDIR/bin/xpauth.xpr
```

 The name of the environment variable used to find shared libraries varies by system; on Linux and Solaris it's usually `LD_LIBRARY_PATH`  and on macOS you should use `DYLD_LIBRARY_PATH`  instead. If unsure, consult your system administrator.
   *  You may find it useful to create a small shell script that sets these variables, or to set them in a script that runs automatically as you log in.

 7. If you plan to use the _xssh_: protocol to connect to a Mosel optimization service running from this installation of FICO Xpress, execute the following commands to generate a unique machine key:
```
cd $XPRESSDIR/bin
./xprmsrv -key new
```



 8. _If you are performing a Linux installation and require the use of dongles for licensing,_ install the dongle drivers now. See  _Dongle Licenses (for Linux Machines)_.

 9. If you are installing a floating server license, you only need a few of the files and can remove the rest. You must keep the following files in order for the XPserver license manager to function correctly:
     * `xpserver` in the `bin` directory.
     * `xplicstat` in the `bin` directory.
     * `runlmgr` in the `bin` directory.
     * All files which begin with `libxprl` in the `lib` directory.
     * `libcrypto.so.3` \( `libcrypto.3.dylib` on macOS\) in the `lib/thirdparty` directory.
     * `libssl.so.3` \( `libssl.3.dylib` on macOS\) in the `lib/thirdparty` directory.
     * The `licensing` directory in the `docs` directory.
     * `xphostid` in the `utils` directory.
     * `license.txt` from the main Xpress installation directory.


 10. To setup the XPserver license manager, follow the instructions as described in [FICO Xpress Licensing](#chapinst2).

### Section 1.9 Patch Installation


Patch, or maintenance, releases are releases that only include updated files for parts of the Xpress software. They may be released to fix a particular bug, improve performance or to add a new feature. The larger maintenance releases can be downloaded from the FICO Xpress website. They are bundled with installers and can be installed by themselves. The patch releases \(which are often individual files or programs\) are usually found on the FICO Xpress download site and must be applied to a previous installation of FICO Xpress.

If you have reported an issue with the software and a fix is now available, you are usually notified by email from the Support system that the fix is available to download using the ftp site and where on the site to download the fix.

#### Windows Patch Installation


 1. Using your zip file extraction program \(such as WinZip or WinRar\) extract the patch files. In most cases, these will be replacements for library or executable files found in the `bin` folder of the Xpress installation, or the `.dso` files found in the `dso` folder of the installation.
 2. If you know where the replacement file\(s\) should be copied, copy them to the correct destination, overwriting the older file. \(You can always rename the older file if you still want access to it.\)
   *  If you are uncertain where the new file should go, search from the Xpress installation directory for the name of the file. To do this, right-click on the Xpress installation folder and select **Search** from the menu. Enter the name of the file you wish to replace in the **All or part of the file name** box and click **Search** . The resulting list indicates where in the Xpress installation the file can be found.

After the patch is placed in the correct location in the installation, the software may be run as normal and the updated files will be automatically used.

_**Note:**  If you plan to install multiple copies of Xpress on one system, make sure that the folder you are applying the patch to is the correct one and that the `XPRESSDIR`, `PATH` and `MOSEL_ DSO` environment variables point towards the correct folders._

#### Linux/Unix Patch Installation


 1. Using your gunzip file extraction and tar archive programs, extract the patch files. On most systems this can be achieved using:
```
gunzip patchfilename.tar.gz
tar xf patchfilename.tar
```

 In most cases, these will be replacements for library or executable files are found in the `lib` and `bin` folders of the Xpress installation, or the `.dso` files found in the `dso` folder of the installation.

 2. If you know where the replacement file\(s\) should be copied, copy them to the correct destination, overwriting the older file. \(You can always rename the older file if you still want to have access to it.\)
   *  If you are uncertain where the new file should go, search on the Xpress installation directory for the name of the file. You can do this using the find command from the Xpress installation directory:
```
find . -name name_of_file_to_be_replaced
```



 3. Running the preceding command results in generating a list of files with matching names. You may find that if you are searching for a particular minor revision of a file, such as `libxprs.so.18.10.05`, that no matching name is found. This is to be expected as the Linux/Unix library files are named as per their revision and contain symbolic links \( `libxprs.so` and `libxprs.so.18.10` in this case\) which point to the actual library file.

After the patch is placed in the correct location in the installation, the software can be run as normal and the updated files will be automatically used.

If you are attempting to install multiple copies of Xpress on one system, ensure that the folder you are applying the patch to is the correct one and that the `XPAUTH_PATH`, `XPRESSDIR`, `PATH`, `LD_LIBRARY_PATH` \(or `DYLD_LIBRARY_PATH` for macOS\) and `MOSEL_ DSO` environment variables point towards the correct folder.

#### macOS Patch Installation


macOS patch releases are provided as a DMG file and contain a complete Xpress installation. Please refer to the instructions at  _Installation on macOS_.

### Section 1.10 Installation of the R and Python packages


The Xpress Optimizer can also be installed as an independent module for languages such as R and Python. The following subsections describe their installation process in detail. We refer the reader to the corresponding reference manuals for a description of the usage of these interfaces.

#### Installation of the R package


The Xpress R Interface is contained as an archive \( `xpress.tar.gz` under Linux and macOS, `xpress.zip` or `xpress.tar.gz` under Windows\) in the installer of the FICO Xpress Optimizer in the R/ subdirectory. It can be installed into an R environment via the R command `install.packages`. Please refer to the file `R/INSTALL.txt` for platform-specific installation instructions.

#### Installation of the Python module


The Xpress Python module can be installed from two Python repositories: The _Python Package Index (PyPI)_ and the _Conda repository_. Installing the Xpress Python interface does _not_ require installation of the whole Xpress suite, as all necessary libraries are provided.

**Xpress 9.9 will be the last release to be published on Anaconda. Subsequent releases of Xpress will be published on PyPI only.** 

The install comes with a copy of the _Community license_, which allows for solving problems with a restricted number of variables and constraints \(see Section  _For Community License_ for details\). If you already have an Xpress license, please make sure to set the `XPAUTH_PATH` environment variable to the full path to the license file, `xpauth.xpr`.

For installation using the PyPI server, run the following on a command line:

```
pip install xpress
```


Packages for several versions of Python are available, for Windows, Linux, and MacOS: see  _Operating System and Hardware_ for a list of supported versions. The package contains the Python interface module, its documentation in PDF format, the Xpress Optimizer's libraries, various examples of use, and a copy of the Community license \(see [https://content.fico.com/xpress-optimization-community-license](https://content.fico.com/xpress-optimization-community-license)\). Online documentation can be viewed at the [FICO Xpress Optimization Help](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/) page.

Packages are also available for free-threading Python 3.14 in beta status. The Xpress Python interface does not yet support parallel threads, so Xpress will re-enable the GIL when it is imported. For more information about free-threading Python, see https://docs.python.org/3/howto/free-threading-python.html.

The above command installs the latest version of the Xpress Python module. Earlier versions of the module can be installed by appending a " `==VERSION` " string to the module name, for instance

```
pip install xpress==9.8.0
```


For Anaconda users, it is recommended to install the PyPI package in your Conda environment, using the `pip` command described above. Alternatively, you can specify the PyPI package in your Conda `environment.yaml` file as demonstrated below:

```
dependencies:
  - python==3.14.*
  - numpy<3
  - pip:
    - xpress==9.9.0
```


A Conda package is available for download with the following command:

```
conda install -c fico-xpress xpress
```


The content of the Conda package is the same as that of the PyPI package. Conda packages are available for Windows, Linux, and MacOS. The Conda installer fetches the latest version of the package but allows for installing earlier versions as in the following example \(note that the Conda installer only uses a single " `=` "\):

```
conda install -c fico-xpress xpress=9.8.0
```


### Section 1.11 Environment Variables Reference


This section provides a comprehensive reference for all user-facing environment variables used by FICO Xpress Optimization. These variables control various aspects of Xpress behavior, licensing, and library loading.

#### Core Xpress Environment Variables



__Environment Variable__ | __Platform__ | __Description__ | 
---------- |  ---------- | ---------- | 
`XPAUTH_PATH` | All | Specifies the path to the Xpress license file or license key location \(applies to both file-based and key-based licenses\). On all platforms, Xpress checks the current directory first. On Windows, the license can also be placed in the `bin`directory. | 
`XPRESSDIR` | All | Specifies the root directory of the Xpress installation. Used primarily for manual installations to locate Xpress components. | 
`PATH` | Windows | On Windows, must include the Xpress `bin`directory for library loading. For convenience, the location of Xpress executables can be added to the path on any platform; executables can also be accessed via explicit paths. | 
`LD_LIBRARY_PATH` | Linux | **Required (Linux).** Specifies the directories to search for shared libraries. Must include the Xpress `lib`directory. | 
`DYLD_LIBRARY_PATH` | macOS | **Required (macOS).** Specifies the directories to search for dynamic libraries. Must include the Xpress `lib`directory. | 

#### Mosel Environment Variables



__Environment Variable__ | __Platform__ | __Description__ | 
---------- |  ---------- | ---------- | 
`MOSEL_ BIM` | All | List of prefixes for locating BIM files \(packages\). Prefixes are separated by `||`and used as prefixes to package names during loading. | 
`MOSEL_ CWD` | All | Current working directory for remote Mosel instances connected via `xprmsrv`. | 
`MOSEL_ DSO` | All | Specifies additional search paths for Mosel modules \(DSO files\) and BIM files \(packages\). Mosel uses a default search path for locating these components \(namely the `dso`subdirectory of the Xpress installation\); any paths specified via `MOSEL_ DSO`will be applied in addition to the default path. | 
`MOSEL_ EXECPATH` | All | Executable paths allowed when `MOSEL_ RESTR`includes NoExec restriction. Specifies programs that can still be executed in restricted mode. | 
`MOSEL_ RESTR` | All | Defines security restrictions for Mosel execution \(used primarily with `xprmsrv`\). Controls access to databases, external processes, and file systems. See[Mosel mmjobs module documentation](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/mosel_lang/dhtml/mmjobs.html?scroll=seccnfxsrv)for configuration details. | 
`MOSEL_ ROPATH` | All | Read-only paths accessible when `MOSEL_ RESTR`includes WDOnly restriction. Similar to `MOSEL_ RWPATH`but read-only access. | 
`MOSEL_ RWPATH` | All | Read/write paths accessible when `MOSEL_ RESTR`includes WDOnly restriction. Specifies directories outside the working directory that can be accessed. | 
`MOSEL_ SDMAX` | All | Sets the maximum size of call stack dumps displayed when a model terminates on a runtime error or assertion failure. Default value of 0 disables stack trace display. Can also be set via command-line option `-sdm`. | 
`MOSEL_ SSL` | All | SSL certificate directory location for secure connections. Default is `~/.mmssl`\(Unix\) or%USERPROFILE%\\ `.mmssl`\(Windows\). | 
`MOSEL_ TMP` | All | Temporary directory for Mosel. If not set, falls back to system temporary directory \( `TMP`, `TEMP`, or `TMPDIR`\). | 
`MOSEL_ TRFILE` | All | Trace file name for Mosel execution tracing. Question mark in filename is replaced by process ID in hexadecimal. | 

#### Platform-Specific Notes


**Windows:** 

 * Environment variables are typically not required if you use the default installation directory and allow the installer to configure the system.
 * The `XPAUTH_PATH` variable is optional on Windows; the license file can be placed directly in the `bin` directory.

**Unix/Linux/macOS:** 

 * Xpress first checks the current working directory for a license file; if not found, it uses the `XPAUTH_PATH` variable.
 * The installer generates setup scripts \( `xpvars.sh` for Bourne shell, `xpvars.csh` for C shell\). Source these scripts \(e.g., `source xpvars.sh` or `. xpvars.sh`\) to set the environment variables in your current shell session.

**Manual Installation:** 

When performing a manual installation \(Section  _Manual Installation_\), you must manually set all required environment variables for your platform. The automated installers handle this configuration automatically.

#### Troubleshooting


If Xpress cannot find the license file or libraries:

 1. Verify environment variables are set correctly for your shell/platform
 2. Ensure the license file exists at the specified `XPAUTH_PATH` location
 3. Check that library directories in `LD_LIBRARY_PATH` / `DYLD_LIBRARY_PATH` exist and contain Xpress libraries
 4. For Mosel issues, verify `MOSEL_ DSO` points to the correct `dso` directory
 5. On Unix/Linux, if using the installer-provided scripts, ensure you have sourced `xpvars.sh` \(Bourne shell\) or `xpvars.csh` \(C shell\) in your current shell session. This step is not required if you configure environment variables through other means \(e.g., system-wide shell profiles\).

For additional troubleshooting, see Chapter  _FICO Xpress Licensing_, Section  _Troubleshooting Licensing Issues_.

### Section 1.12 GPU installation guidelines for PDHG


The primal-dual hybrid gradient \(PDHG\) linear optimization solver can now take advantage of a NVIDIA® CUDA® -capable GPU, if present. The GPU support for PDHG is available as a beta release with Xpress 9.9. The following platforms have been tested: Linux \(both x86\_64 and ARM64\) and Windows \(x86\_64\).

**Software requirements:** 

 * 
At least version 580 of the NVIDIA drivers must be installed. The latest version is available from [https://www.nvidia.com/drivers](https://www.nvidia.com/drivers).

 * 
At least version 13.0 of the NVIDIA CUDA Runtime must be installed. The CUDA Toolkit, which includes the Runtime, can be downloaded from [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads).


These steps can be performed either before or after the installation of Xpress. After a successful installation, the required libraries are automatically picked up by Xpress.

When installing the Xpress Python package, the required CUDA Runtime dependencies can also be installed from PyPI or Conda:

 * 
When installing Xpress from PyPI, the CUDA Runtime can be specified as an optional dependency:

```
pip install xpress[cuda]
```



 * 
When installing Xpress from Conda, the CUDA Runtime can be installed using the following command:

```
conda install -c nvidia cuda-cudart libcusparse libcublas
```



**When starting the hybrid gradient solver \( `BARALG=4`\), you need to specify `BARHGGPU=1` to use the GPU.**  The solver will then check the availability of the CUDA libraries and the presence of a GPU, and will print a message to the log.

**Note:**  The GPU-enabled hybrid gradient algorithm cannot be used in the deterministic concurrent solver.

## Chapter 2 FICO Xpress Licensing


### Section 2.1 Introduction


This chapter describes the licensing configuration options and types of licenses available for using FICO Xpress.

**Note:**  For the purposes of this guide, Option\_1 \(Node Locked\), Option\_2 \(USB Dongle\), and Community licenses are referred to as "static" licenses. Option\_3 \(Floating\) licenses are referred to as "floating" licenses, and Option\_4 \(Web Floating\) licenses are referred to as "web floating" licenses.

#### Community License


The Community license enables development, modeling, and deployment of the industry leading FICO Xpress Optimization software, free of charge. It can be enabled during installation on Windows; it is automatically enabled during installation on macOS. The solvers in the Community license are limited in problem size. In this edition, the sum of the number of rows \(constraints\) and columns \(variables\) is restricted to 5000 for linear and mixed-integer problems, and is restricted to 200 for quadratic and general nonlinear problems. In addition, the number of nonlinear tokens \(measure of the complexity for nonlinear expressions\) is restricted to 1000, and the number of user functions \(black-box optimization\) is restricted to 1. You can unlock these capabilities by purchasing and installing a full license.

#### Full License


You can obtain a license file or key from FICO Sales \(or your Xpress supplier\). The full license removes the problem size limits imposed by a Community license. This applies to both new users and users upgrading from earlier releases.

There are two possible formats for a full Xpress license:

 * **License file (compatible with all Xpress versions):** 
     * **Format** : A file called `xpauth.xpr` that contains the list of enabled features.
     * **Applies to:**  Static and Floating Licenses.
     * **Version** : Applies to all versions including current versions.
     * **Activation** : Requires running the Xpress Host ID tool and sending that information to FICO in order to obtain the license file.

**Note:**  _Licensing via license files will be phased out in future releases. License keys will become the standard method for activating and managing licenses._

Static and Floating license files are generated using information from the output of the **Xpress Host ID**  tool. If you are requesting a static license, run the tool using the following procedure on the machine that will host the installation. For a floating license, follow the steps to run the tool on the server.

     * Using Microsoft Windows, you can run this tool from the Start menu, or by browsing in Windows Explorer to navigate to the `< installationdir>\bin` folder and double clicking `xphostid.exe`.
     * If you use Unix, the tool is installed in the `< installationdir>\bin` folder as `xphostid`.

If you are upgrading from an earlier release, you must also supply the order reference number or ASSC \(support\) reference number.

 * **License key (introduced in Xpress 9.6):** 
     * **Format** : A license key that you receive via email, along with `Oauth2` credentials that you generate from your user portal \(see Section  _The License Spring Portal and How to Retrieve the OAuth2 Credentials_\).
     * **Applies to:**  Static and Web Floating Licenses.
     * **Version** : Xpress release 9.6 and above for Web Floating licenses, Xpress release 9.8 and above for Static licenses.
     * **Activation** : A specific activation step is not required. Simply running the Solver will activate the license, assuming the license key and `OAuth2` credentials are properly configured \(see Section  _The License Spring Portal and How to Retrieve the OAuth2 Credentials_\).

**Note:** . The new license key format will only be backwards compatible until release 9.6.


Both license files and license keys authorize the use of all minor releases within a major release. For example, a license file/key for Xpress 9.7 authorizes the use of all 9.7 minor releases \(9.7.1, 9.7.2, and so forth\). A new license file would be required for a new major release such as Xpress 9.8. License keys are automatically updated for Web Floating licenses, refer to Section  _Managing a Key-based Static License with the xplicsync Utility_ to refresh a key-based Static license.

### Section 2.2 Using a File-based Static License


**Note:**  This section applies to Option\_1 \(Node-locked\) and Option\_2 \(USB Dongle\) licenses.

 1. Install the license file \( `xpauth.xpr` \) that you received from FICO Support by saving/copying the file into your `xpressmp\bin` directory.
   *  For UNIX machines, copy the `xpauth.xpr`file into a convenient directory, such as `xpressmp/bin`, and set the `XPAUTH_PATH`environment variable to the full path:
```
bash$ export XPAUTH_PATH=/opt/xpressmp/bin/xpauth.xpr
csh% setenv XPAUTH_PATH /opt/xpressmp/bin/xpauth.xpr
```

The `XPAUTH_PATH` environment variable is only used by Xpress to find the license file. On Windows `XPAUTH_PATH` is not needed, since by default Xpress looks for `xpauth.xpr`in the directory containing the Xpress libraries, `xpressmp\bin`. We recommend that `XPAUTH_PATH` is not set on Windows, in order to keep the installation simple.

 2. You are now ready to use the Xpress product.

_**Note:**  Previous releases of Xpress used the `XPRESS` environment variable to locate the license file on UNIX machines. This is now deprecated in favour of the `XPAUTH_PATH` environment variable. When upgrading, please update any existing user scripts which set `XPRESS` so that they instead set `XPAUTH_PATH`._

### Section 2.3 Using a File-based Floating License


**Note:**  This section applies to Option\_3 \(Floating\) licenses. This license type can only be used with a file-based format.

A floating license requires a license manager to be run on a designated machine that is called the _license server_. Any instance of Xpress that is started on any machine contacts the license server over the network for authorization before continuing. This guide refers to those machines running Xpress as _client machines_.

#### Setting Up the License Manager


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

 1. To use a floating license, you must designate a machine on your network to be the license server. This machine must allow incoming connections on TCP port 27100 \(or another of your choice as described in the section  _Custom Port Number_\).
 2. Run the Xpress installer on the server machine. The installer is a wizard that step you through the installation process.
     * On UNIX machines you will be prompted for a license file. Enter the path to the folder containing the file `xpauth.xpr` that you received from FICO Support. The license file will automatically be copied into the server installation.
     * On Microsoft Windows machines you will be asked whether to install the license manager as a Windows service. To install the license manager as a service you must have Administrator privileges, so if you do not have Administrator privileges choose **No**  when prompted.

 3. _For Microsoft Windows installations only:_ Copy the server license file you received from Xpress Support \( `xpauth.xpr`\) into the `bin` folder of Xpress installation directory.
 4. Before you run Xpress on any of the client machines, start the license manager on the server.
     * On Windows, use the shortcut on the Start menu to start the license manager. If you installed the license manager as a Windows service you can also start and stop it using the Services control panel applet.
     * You can also start the license manager from a Unix shell or Windows command prompt \(or DOS box\) using one of the following commands:


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`runlmgr start` | \(for the standalone license manager and the Unix license manager\) | 
`runlmgr starts` | \(for the license manager Windows service\) | 


The license manager remains running until you stop it manually or restart the computer, in which case it will need to be restarted before Xpress can be used again.

#### Setting Up the Clients


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

 1. To set up a client machine to use a floating license, you must first install Xpress on the client machine. When the installer asks you whether this is a server machine or a client, choose client. Enter the path where you want to install Xpress.
 2. During installation you will be prompted to enter the hostname of your license server. Enter the hostname of your machine, together with any qualifying domain if necessary. For example:
```
uranos.ficdash.co.uk
```



**Note:**  It is not necessary to run the license manager on the client machines.

#### Using the Client and Server on the Same Machine


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

 * To run the Xpress software on your server machine: Install the client and server in different folders. Install the client first \(as described earlier\) and then install the server. When prompted for an install path, enter a different path.
 * To install the client and server into the same folder: Install the client first, and then the server. You may also have to edit the `use_server` line of your license file to point the client at your local machine, since both client and server will use the same license file for this type of configuration.

#### Stopping the License Manager


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

At times you may wish to take your license server process offline, for maintenance or upgrade purposes, for example.

 * On Windows, you can stop \(and start\) the license server using the links placed in the Xpress area of the Start menu.
 * If you are using a Unix machine \(or for Windows users who do not/cannot use the Start menu option just described\) you can control the license server using the `runlmgr` script manager from a Unix shell or Windows command prompt \(or DOS box\):
 


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
`runlmgr stop` | \(for the standalone license manager and the Unix license manager\) | 
`runlmgr stops` | \(for the license manager Windows service\) | 


#### Custom Port Number


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

You may need to configure the license manager to use a particular TCP port, such as in those cases where you are running another service on your server machine which is conflicting with the Xpress license manager, or if you want to make a rule in your firewall to allow incoming connections on this port. Use the following instructions to do so:

 1. Edit the license file on the server and add a `server` line specifying the port number. For example:
```
server port="12840"
```



 2. Edit the license file on the client and add the following `port` directive to the `use_server` line. For example:
```
use_server server="our_server_machine" port="12840"
```



 3. Restart the license server application in order for it to re-read the license file.

#### Encrypting Network Communications


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

When possible, communications between the client and the license server are encrypted using Transport Layer Security \(TLS\) version 1.3. This feature requires that the OpenSSL libraries are present in both the application and the license server. \(See  _Creating FICO Xpress Runtime Distributions_ for a list of library files.\) If the OpenSSL libraries cannot be located, encryption will be disabled.

In high security environments you may want to ensure that network communication is always encrypted. To do this, use the following instructions:

 1. Edit the license file on the server and add a `server` line with the following `tls` directive:
```
server tls="always"
```



 2. Edit the license file on the client and add the following `tls` directive to the `use_server` line:
```
use_server server="our_server_machine" tls="always"
```



 3. Restart the license server application in order for it to re-read the license file.

#### Connection Retries


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

In some cases, where the license server resides on a high-traffic machine or you have a large number of client applications, it may be helpful to automatically retry failed connections. Using this feature, if a client fails to connect to a license server, it will retry for a specified number of attempts, leaving an exponentially increasing delay between retries, rather than returning an error. To do this, follow the following instructions:

 1. Edit the license file on the client and add the `retries` directive to the `use_server` line. For example, to retry a failed connection 5 times before returning an error:
```
use_server server="our_server_machine" retries="5"
```



#### Logging


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

By default the license server process creates a log file called `xprl_server.log` in a temporary folder on the server machine.

 * On Windows machines, the server logfile is created in the temporary folder by default, which is typically the folder `Local Settings\Temp` within the profile of the user account used to run the server; however in some circumstances it may appear in `C:\Windows\Temp`.
 * On Unix machines the server logfile is generally found in either `/tmp` or `/var/tmp`.

To fine-tune the server's logging: edit the server license file and add a `logging` line. For example, you can change the location of the logfile as follows:

```
logging file="C:\logs\xprl_server.log"
```


or on Unix machines:

```
logging file="/var/log/xprl_server.log"
```


To change the level of detail that will be placed in the log file, use the `logginglevel` command. For example:

```
logging level="verbose"
```


The default detail level is `normal`. Other levels are `quiet` \(log only serious errors\), `verbose` \(log more detail than `normal`\) and `debug` \(which should only be used under the direction of FICO support\).

To change the log file size: By default the log file should not get much larger than 128 kilobytes; if you find this is not enough and want to store more logging data you can set the `maxsize` directive to the number of kilobytes you want to retain. For example:

```
logging maxsize="256"
```


#### License Status


**Note:**  This section applies to Option\_3 \(Floating\) licenses.

When using a server license, you may want to quickly review the current state of all the licenses. For example, you may want to find out who is using a license that you want to use yourself.

You can use the supplied command-line tool `xplicstat` to summarize which licenses are in, as well as which tokens can still be checked out. For floating licenses only, the tool will also output the time the license was locked and the IP address of the machine that locked it. Use the `xplicstat` command in conjunction with a client `xpauth.xpr` file and at least one `use_server` line.

This command will use the `XPAUTH_PATH` environment variable to locate the license file. On Windows, if `XPAUTH_PATH` is not set, the command will look for the license file in the same folder as the executable. You can also specify an alternate location using the `-xpress` command-line flag. For example:

```
xplicstat -xpress C:\xpressmp\bin\xpauth.xpr
```


#### Replacing the License File


If you need to upgrade or renew your license, contact FICO Support to send you a new `xpauth.xpr` file, which you must place in the same location as the original `xpauth.xpr` as follows:

 * For Option\_1 \(Node Locked\) or Option\_2 \(USB Dongle\) licenses, this location is in the `bin` sub-folder of the Xpress installation.
 * For Option\_3 \(Floating\) licenses, you must place it in the `bin` subfolder of the Xpress server installation on the server machine. Restart the server process in order to force the server to reread the license file.

### Section 2.4 Using Key-based \(Static or Web Floating\) Licenses


**Note:**  This section applies to Option\_1 \(Node Locked\) and Option\_4 \(Web Floating\) licenses.

Static and Web Floating licenses using license keys allow users to activate their license via a license manager hosted by FICO. When a user needs to activate \(Static license\) or use \(Web Floating license\) the software, the license is checked out from the web server using a license key and `OAuth2` credentials.

**Note:**  The license keys associated with a Web Floating License can only be used from Xpress 9.6 onwards. Support for key-based Static licenses was introduced in Xpress 9.8.

#### Activation


**Note:**  This section applies to Option\_1 \(Node Locked\) and Option\_4 \(Web Floating\) licenses.

To activate a key-based Static or Web Floating license with FICO Xpress, a JSON-formatted file is necessary. We recommend naming the new license file as `xpauth.xpr`, replacing the existing file in the Xpress installation directory, although the license file can have any name and extension \(  _e.g._  `config.json`\). In any case, its contents must have the structure described below. Please make sure to set the environment variable `XPAUTH_PATH` to point to the full path to this file.

The JSON-formatted license file must contain two main key-value pairs: an _oauth2_ key that points to the client ID and client secret key-value pair for Open Authorization \( _OAuth2_\), which can be obtained via the License Spring portal \(see Section  _The License Spring Portal and How to Retrieve the OAuth2 Credentials_\). The _license_ key refers to a 19-character string, with the format "AAAA-BBBB-CCCC-DDDD".

```
{
		"oauth2": {
				    "client_id": "your_client_id",
				    "client_secret": "your_client_secret"
		},
		"license": "AAAA-BBBB-CCCC-DDDD"
}
```


**Note:**  Please use only one key \(19-character string in the "licenses" section\) per license file, and ensure that the license key in the JSON file is surrounded by double quotes, as pictured above.

While Static licenses use a cache system on the device and do not require a persistent internet connection, Web Floating licenses can be used and shared by multiple users and therefore will be checked out from the web server on every use.

In addition, please make sure that the following domains are allowlisted by your IT/Cybersecurity department, if applicable:

 * [api.prod.fico.licensespring.com](https://api.prod.fico.licensespring.com)
 * [saas.prod.fico.licensespring.com](https://saas.prod.fico.licensespring.com)
 * [users.prod.fico.licensespring.com](https://users.prod.fico.licensespring.com)
 * [auth.prod.fico.licensespring.com](https://auth.prod.fico.licensespring.com)

For simplicity, it may be easier to simply allowlist `*.prod.fico.licensespring.com` if your system allows you to do so.

For offline and air-gapped licenses, please allowlist the following domains, respectively:

 * [licensing-offline.fico.com](https://licensing-offline.fico.com)
 * [licensing-airgap.fico.com](https://licensing-airgap.fico.com)

**Note:**  if you intend to run Xpress using a key-based license inside **Docker containers** , keep in mind that a Static license will be bound to the container it is first activated in, failing to initialize in subsequently created containers. It is therefore recommended to acquire a Web Floating license for such use cases, unless you intend to run the software inside a long-lived Docker container with lifecycle management practices.

#### The License Spring Portal and How to Retrieve the `OAuth2` Credentials


**Note:**  This section applies to Option\_1 \(Node Locked\) and Option\_4 \(Web Floating\) licenses.

The License Spring portal is a web platform designed to manage software licensing for digital products. You can manage your Static or Web Floating licenses for Xpress via this portal.

 * Sign in to the [License Spring portal](https://licensing.fico.com) using your account details.
 

![install15.png](Graphic/install15.png)



 * After login, you will be shown the **Dashboard**  page with your role and the number of licenses associated with your account.
 

![install16.png](Graphic/install16.png)



 * On the left panel, click on **Licenses**  to visualize a detailed list of currently available licenses in your account.
 

![install17.png](Graphic/install17.png)



 * Click on any field of the license entry \(row\) to access the details of the license you want to manage. By default, the **License details**  tab is shown. This view contains important information about the license, such as the current status, the maximum number of users, or the floating timeout value.
 

![install18.png](Graphic/install18.png)



 * Select the **Product features**  tab to get an overview of the features/tokens included in the license.
 

![install19.png](Graphic/install19.png)



 * Click on the **Custom fields**  tab to see additional specifications relative to your license.
 

![install20.png](Graphic/install20.png)



 * The **Devices**  tab shows the characteristics of the devices where the license has been used.
 

![install21.png](Graphic/install21.png)



 * To initialize and retrieve the _OAuth_ credentials, open the **OAuth**  tab and click on the _Initialize OAuth_ button:
 

![install22.png](Graphic/install22.png)


 
Once the credentials have been initialized, you can use the respective _copy_buttons to copy and paste the values of your client ID and client secret into your license file.
 

![install23.png](Graphic/install23.png)


 
Moreover, there are three options available on the dashboard appearing after the _OAuth_credentials have been initialized:
 * _Refresh_: This action will invalidate the current client secret and generate a new one. Any applications using the current secret will stop working until they have been updated.
 * _Rotate_: Use this button to define the secret expiration period \(time passed before a newly generated secret expires\). It is possible to define a grace period \(period of validity\) for the current secret.

 

![install24.png](Graphic/install24.png)


 
 * _Delete_: This action deletes the current _OAuth_ credentials entirely, requiring a new credential initialization for the license key to be used.
 **Note:** Please remember to keep the license key and **OAuth** credentials confidential, limiting their possession to the intended user\(s\).

#### Managing a Key-based Static License with the `xplicsync` Utility


**Note:**  This section applies to Option\_1 \(Node Locked\) licenses.

Static licenses using a license key format offer the flexibility to be deactivated on one device and activated on another device a limited number of times. To this end, use the `xplicsync` utility in your `xpressmp\bin` directory, which provides a series of flags to activate/deactivate/refresh your license using your license key and `OAuth2` credentials \(see how to retrieve those in Section  _The License Spring Portal and How to Retrieve the OAuth2 Credentials_\).

There are two possible ways to authenticate when running a command with the `xplicsync` utility:

 * Using the license key and credentials contained in your `xpauth.xpr` file:

```
xplicsync --config /path/to/xpauth.xpr <flag>
```

 * Using the license key and `OAuth2` credentials within the command:

```
xplicsync --key <YOUR_KEY> --client_id <YOUR_ID> --client_secret <YOUR_SECRET> <flag>
```


In the remainder of this section, we use the first method for demonstration purposes.

 * **To deactivate a license linked to a device** , invoke the utility with the `deactivate` flag on the device where the license is active:
```
xplicsync --config /path/to/xpauth.xpr --deactivate
```



 * **To activate a license on a new device** , run the utility with the `activate` flag on the new device:
```
xplicsync --config /path/to/xpauth.xpr --activate
```

 You can also use this method to do the first activation of your license as an alternative to Section  _Activation_.

 * **To refresh your license**  after, for example, you had an upgrade to your features or expiry date, invoke the utility with the `refresh` flag:
```
xplicsync --config /path/to/xpauth.xpr --refresh
```

 This will synchronize the local license with the updated information on the web server.

**Note:**  A node-locked license is contractually assigned to a single machine and a technical limit is imposed how often such transfers can occur. Please contact FICO support or FICO sales in case you reach that limit.

**Note:**  Static licenses data are stored in a cache on your device. Cache location depends on the OS type:

 * Windows:

```
<SystemDrive>:/Users/<UserName>/AppData/Local/LicenseSpring/XpressSolver/<LIC_KEY>.lic
```

 * Linux:

```
<HOME>/.LicenseSpring/LicenseSpring/XpressSolver/<LIC_KEY>.lic
```

 * MacOS:

```
~/Library/Application Support/LicenseSpring/XpressSolver/<LIC_KEY>.lic
```


#### Activate Offline Static License


**Note:**  This section applies to Option\_1 \(Node Locked\) licenses.

Any static license can be activated in `offline` mode in case, for example, the license needs to activated on a device without an internet connection. To do so, you can use the `xplicsync` utility \(see Section  _Managing a Key-based Static License with the xplicsync Utility_\).

 * **Step 1** : Generate a `request` file using `xplicsync` **on the device where the license is meant to be used** .
```
xplicsync --key <YOUR_KEY> --client_id <YOUR_ID> --client_secret <YOUR_SECRET> --offline_initialize --request_file <REQUEST_FPATH>.req
```

 Where `<REQUEST_FPATH>` is the path you seek the `request` file to be generated to. Note that the file **must**  have the **.req**  extension.

 * **Step 2** : Upload the `request` file into the [Offline Licensing Portal](https://licensing-offline.fico.com/) **on any device with an internet connection** .
 

![activateoffline.png](Graphic/activateoffline.png)


 
This will generate a **.lic** license file called the `response`file.

 * **Step 3** : Register the `response` file **on the device where the license is meant to be used** . Transfer the `response` file to the device and place it in a `<RESPONSE_FPATH>` path to your choosing.
```
xplicsync --key <YOUR_KEY> --offline_activate --response_file <RESPONSE_FPATH>
```

 Your static license is now ready to use\!

**Note:**  All of the above commands using `xplicsync` can also be used with the **JSON config file**  as described in section  _Managing a Key-based Static License with the xplicsync Utility_.

**Note:**  Offline-activated licenses can be used as regular static licenses and even refreshed, as described in section  _Managing a Key-based Static License with the xplicsync Utility_.

#### Activate Air-Gapped Static License


**Note:**  This section applies to Option\_1 \(Node Locked\) licenses.

Air-gapped licenses are **purely offline**  licenses, useful for devices operating in a completely disconnected environment, physically isolated from any external networks.

 * **Step 1** : Initialize the Airgap process on **any device with an internet connection** . Feed your license key to the [Airgap Licensing Portal](https://licensing-airgap.fico.com/) by clicking on the **Initialize air-gap activation**  button.
 

![airgapactivate1.png](Graphic/airgapactivate1.png)


 
This will generate an `airgap_initialization_code`.

 * **Step 2** : Generate an `airgap_activation_code` and `hardware_id` using the `xplicsync` utility **on the device where the license is meant to be used** . Use the `airgap_initialization_code` you have received in the previous step to generate an `airgap_activation_code`.
```
xplicsync --key <YOUR_KEY>
        --airgap_activation_init
        --airgap_initialization_code <airgap_initialization_code>

```

 **Note:**  Both the `airgap_activation_code` and `hardware_id` values will be needed for the next step.

 * **Step 3** : Initialize the Airgap **confirmation**  process on **any device with an internet connection** . Enter your `hardware_id` and the `airgap_activation_code` generated in the previous step in the [Airgap Licensing Portal](https://licensing-airgap.fico.com/) by clicking on the **Enter air-gap activation code**  button.
 

![airgapactivate2.png](Graphic/airgapactivate2.png)


 
This will generate an `airgap_confirmation_code`as well as the `license_policy_id`needed for the next step.

 * **Step 4** : Activate the Air-Gapped license **on the device where the license is meant to be used** . For this step, you will also need an `airgap_public_key` and the License's `airgap_policy_file`. Please reach out to FICO support if you cannot find any of these two fields on the **License details**  tab of the Licensing Portal.
 

![airgappolicy.png](Graphic/airgappolicy.png)


 
Make sure to save the policy file on your device in a chosen `<POLICY_FPATH>`, and then run the command below.
```
xplicsync --key <YOUR_KEY>
        --airgap_activate
        --airgap_confirmation_code <airgap_confirmation_code>
        --license_policy_id <license_policy_id>
        --airgap_public_key <airgap_public_key>
        --airgap_policy_file <POLICY_FPATH>

```

Your static license is now ready to use\!

#### Deactivate Air-Gapped Static License


**Note:**  This section applies to Option\_1 \(Node Locked\) licenses.

The Airgap deactivation form can be reached from the [Airgap Licensing Portal](https://licensing-airgap.fico.com/) by clicking on the green switch.


 


![airgapdeactivate0.png](Graphic/airgapdeactivate0.png)



 


![airgapdeactivate1.png](Graphic/airgapdeactivate1.png)



 


 * **Step 1** : Initialize the Airgap process on **any device with an internet connection** . Feed your license key to the [Airgap Licensing Portal](https://licensing-airgap.fico.com/) by clicking on the **Initialize air-gap deactivation**  button.
 

![airgapdeactivate2.png](Graphic/airgapdeactivate2.png)


 
This will generate an `airgap_initialization_code`.

 * **Step 2** : Generate an `airgap_deactivation_code` and `hardware_id` with `xplicsync` **on the device where the license is currently active** . Use the `airgap_initialization_code` from the previous step to generate an `airgap_activation_code`.
```
xplicsync --key <YOUR_KEY>
        --airgap_deactivation_init
        --airgap_initialization_code <airgap_initialization_code>

```



 * **Step 3** : Initialize the Airgap **confirmation**  process on **any device with an internet connection** . Use your `hardware_id` and the `airgap_deactivation_code` generated in the previous step in the [Airgap Licensing Portal](https://licensing-airgap.fico.com/) by clicking on the **Enter air-gap activation code**  button.
 

![airgapdeactivate3.png](Graphic/airgapdeactivate3.png)


 
This will generate an `airgap_confirmation_code`as well as the `license_policy_id`, which will be needed for the next step.

 * **Step 4** : Dectivate the Air-Gapped license **on the device where the license is currently active** . For this step, you will also need an `airgap_public_key` and the License's `airgap_policy_file`. Please reach out to FICO support if you cannot find any of these two fields on the **License details**  tab of the Licensing Portal. Make sure to save it on your device in a chosen `<POLICY_FPATH>`.
```
xplicsync --key <YOUR_KEY>
        --airgap_deactivate
        --airgap_confirmation_code <airgap_confirmation_code>
        --license_policy_id <license_policy_id>
        --airgap_public_key <airgap_public_key>
        --airgap_policy_file <POLICY_FPATH>

```

 Your static license is now removed from your device\!

#### License Configuration File Options


The JSON-formatted license file described in Section  _Activation_ supports an optional _options_ field that allows you to customize the behavior of the licensing system. This field can be added to both Static and Web Floating licenses.

The _options_ field supports the following parameters:

 * **floating_timeout_ratio** – Controls the floating license check-in frequency \(Web Floating licenses only\)
 * **licensing_home** – Specifies a custom directory for storing license cache files

##### Option floating\_timeout\_ratio


**Applies to:**  Web Floating licenses \(Option\_4\) only. This option is ignored for Static licenses.

**Type:**  _float_

**Default value:**  1.0

Since Web Floating licenses can be shared by multiple users, they will be checked out from the web server on every use. A license will be released for other users when it has not been checked in the server for a time defined as _Floating timeout_. The timeout duration can be consulted in the _License details_ tab of the LicenseSpring portal \(see  _The License Spring Portal and How to Retrieve the OAuth2 Credentials_\).

The _floating_timeout_ratio_ is a multiplier that adjusts the interval at which the license is checked for availability on the licensing server. This value works as a multiplier to the default floating timeout configured for your license on the LicenseSpring platform.

For example, if your license has a default floating timeout of 10 minutes and you set _floating_timeout_ratio_ to 1.5, the effective timeout becomes 15 minutes. This means the solver will connect to the server every 15 minutes during an optimization run to indicate that the license is still in use.

**Important notes:** 

 * The minimum effective timeout is 1 minute. Values that result in timeouts below 1 minute will be clamped to 1 minute.
 * Users can only _increase_ the timeout, not decrease it. The system will use the maximum of the calculated value and the license's base timeout.
 * Increasing the timeout reduces network traffic and API calls to the licensing server, but also delays license reclamation when a user stops using it.

Example configuration:

```
{
    "oauth2": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret"
    },
    "license": "AAAA-BBBB-CCCC-DDDD",
    "options": {
        "floating_timeout_ratio": 1.5
    }
}
```


**Note:**  In case the internet connection is interrupted and the floating timeout period has elapsed, the license will become inactive locally and is released for other users. Note that, in this case, you will not be able to resume an ongoing optimization run, as Xpress will need to be re-launched for re-activating the license.

##### Option licensing\_home


**Applies to:**  All license types \(Static and Web Floating\).

**Type:**  _string_ \(file path\)

**Default value:**  Platform-dependent system directory

The _licensing_home_ option allows you to specify a custom root directory where license cache files and related data are stored. By default, the licensing system stores license files in platform-specific system directories.

**Default locations:** 

 * **Windows:**  `<SystemDrive>:/Users/<UserName>/AppData/Local/LicenseSpring/XpressSolver/`
 * **Linux:**  `<HOME>/.LicenseSpring/LicenseSpring/XpressSolver/`
 * **MacOS:**  `~/Library/Application Support/LicenseSpring/XpressSolver/`

When you set _licensing_home_, this custom path replaces the entire default directory structure. The licensing system will create subdirectories and store license files \(named `<LIC_KEY>.lic`\) in this location.

**Use cases:** 

 * multi-user systems where licenses should be accessible to all users
 * containerized or virtualized environments with persistent volume mounts
 * network installations requiring centralized license management
 * systems with restricted filesystem permissions
 * testing or CI/CD environments with temporary directories

**Important notes:** 

 * The specified directory must exist and be writable by the application.
 * Absolute paths are recommended to avoid ambiguity.
 * The licensing system automatically creates subdirectories for individual license keys.

Example configuration with custom license storage:

```
{
    "keys": {
        "api_key": "your_api_key",
        "shared_key": "your_shared_key"
    },
    "license": "AAAA-BBBB-CCCC-DDDD",
    "options": {
        "licensing_home": "/opt/xpress/licenses"
    }
}
```


In this example, license files will be stored in `/opt/xpress/licenses/XpressSolver/` instead of the default system location.

You can combine both options in a single configuration file:

```
{
    "oauth2": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret"
    },
    "license": "AAAA-BBBB-CCCC-DDDD",
    "options": {
        "floating_timeout_ratio": 1.5,
        "licensing_home": "/opt/xpress/licenses"
    }
}
```


#### Using Key-based Licenses in Jupyter Notebooks \(Python\)


**Note:**  This section applies to Option\_1 \(Node Locked\) and Option\_4 \(Web Floating\) licenses.

If you are running Jupyter notebooks locally or in \(remote\) virtual environments \(  _e.g._  Google Colab or GitHub Codespaces\), you can use a Static or Web Floating license in the notebook context without the need to explicitly manage a license file \(note that using a file as described in Section  _Activation_ is also possible\).

In your Jupyter notebook, you can create a Python dictionary that stores the license key and `OAuth2` credentials in memory and pass it down to Xpress as a string, as shown in the picture below.

![install25.png](Graphic/install25.png)


This will activate the license for the current notebook until

```
xp.free()
```


### Section 2.5 Troubleshooting Licensing Issues


If there is a problem with your Xpress license, the error message provides information about the problem.

For floating licenses, also check the `xprl_server.log` log file for any recent error messages. If the license server fails to start, check the Windows event log \(or `/var/log/messages` on Unix systems\) for any errors.

Refer to the following section  _Licensing Error Messages and Suggested Resolutions_ for common errors and probable causes and/or resolutions.

If you do not resolve the problem by reviewing this section, try the following steps:

 1. Upgrade to the latest version of Xpress.
 2. If you have a portable Windows machine with a license tied to your Ethernet address, and you are having problems when the machine is not connected to a network, it may have _Media Sense_ enabled. This disables the Ethernet card when no network is connected to save power. Disable Media Sense by following the instructions on Microsoft's website: [http://support.microsoft.com/default.aspx?scid=kb;EN-US;q239924](http://support.microsoft.com/default.aspx?scid=kb;EN-US;q239924).
 3. If you are running Windows XP and the Xpress host ID tool does not show any host IDs, your network adapters may be bridged. To fix this, use the Control Panel and select **Network and Internet Connections** , and click **Network Connections**  \(depending on your set-up, you may instead have to double-click Network Connections as soon as you open the Control Panel\). If the window contains a section entitled Network Bridge, right click the Network Bridge icon and choose **Delete** . Now re-run the Xpress host ID tool to find out the host ID of your computer.

If you still have problems, please contact FICO Support, giving full details about the error number and message obtained, along with a description of the circumstances under which it occurred.

### Section 2.6 Licensing Error Messages and Suggested Resolutions


These error messages are displayed by executable software, including Xpress Workbench, Optimizer console, and Mosel console. If you are using any of the Xpress libraries, the error message can be obtained using the `XPRSgetlicerrmsg`  \(Optimizer\) or `XPRMgetlicerrmsg`  \(Mosel\) functions. For floating licenses they may also show in the `xprl_server.log`  log file.

If you obtain an error number not listed here, report the error number and message to FICO Support, along with a description of the circumstances under which it occurred.

 * __1__   __*The license file \(xpauth.xpr\) could not be found.*__
   Make sure you have the correct license file in the correct location. Under Windows, the `xpauth.xpr` file should be placed in the Xpress bin directory \(the directory on the path containing the Xpress DLLs\). If you are using the `XPAUTH_PATH` environment variable on Windows, check that it is set to the full path to your license file. \(We recommend not setting `XPAUTH_PATH` on Windows, and instead placing `xpauth.xpr` in the Xpress bin directory.\) Under Unix, the `XPAUTH_PATH` environment variable must be set to the full path of the `xpauth.xpr` file.
   *   _**Note:**  Previous releases of Xpress used the `XPRESS` environment variable to locate the license file. This is now deprecated in favour of the `XPAUTH_PATH` environment variable. When troubleshooting licensing issues, make sure that `XPRESS` is not set._
 * __2__   __*There is an error in your license file...*__
   or
 * __8__   __*Your license file has not been signed by Xpress Support / has an incorrect signature.*__
   or
 * __11__   __*Your license is invalid as it specifies an invalid / no expiry date.*__
   Your license file is corrupt— try replacing it with the license file originally sent to you by FICO Support. If the original license file sent to you is invalid, then request a new license file. Attach the corrupted license file and provide the error code number— this indicates to FICO Support exactly what is wrong with the file.
 * __4__   __*The maximum number of simultaneous users has been reached.*__
   Your license file specifies a limit on the number of copies of Xpress that can be used simultaneously and that limit has been reached. Close one of the copies of Xpress, or wait until another user has finished with Xpress, or upgrade your license.
 * __9__   __*The license file only supports host ID\(s\)\(id1,...\)*__
   Your license is locked to a different host from that which you are trying to run Xpress \(or for floating licenses, the license is locked to a different server machine from the one you are using\). If you need a license for this machine, contact Xpress Support.
   *  If you receive error# 9 and you are sure your license is locked to your machine's hostid, it may be that Xpress cannot detect your hostid. If you have an Ethernet license, disable _Media Sense_, as described earlier in this section. If you have a dongle, make sure that it is plugged in and to manually install the dongle drivers from your latest Xpress installation, as described in the section  _Installing the HASP Dongle Device Driver_.
 * __10__   __*Your license expired on\(date\).*__
   Your license has expired. Contact FICO Support to renew it or to obtain an upgrade.
 * __14__   __*Could not connect to server...*__
   Check that the server computer is visible over the network. Enter the following command:
```
ping name_of_license_server
```

 Also, verify that the license server application, `xpserver`, is currently running on the server machine. Check the logfile for errors. If you have a firewall, ensure that it is not blocking communications to and from the Xpress license server application.
 * __20__   __*License could not be checked out on redundant servers.*__
   A quorum \(two out of three\) of redundant license servers could not be obtained for this license. Either insufficient redundant license servers are active, or the license is already checked out on the other two redundant license servers. _(This error can only occur when using a redundant server license.)_
 * __21__   __*Your license only supports release\(rel\).*__
   Your license is for a previous release of Xpress. Be sure that you are not using an old license and that Xpress is finding the correct license file by following the suggested resolution in \(# `2`\) above.
   *  If your license only covers a previous release, contact FICO Support to upgrade it.
 * __89__   __*Your license only supports platform\(s\)\(plat1,...\).*__
   Your license file does not support the platform that you are using to run Xpress. Contact FICO Support if you want to upgrade.
 * __90__   __*TLS requires a license server with version at least...*__
   Your license file specifies that communication with the license server is encrypted with TLS, but the license server does not support this feature. Ensure that the license server application, `xpserver.exe`, is taken from Xpress version 9.2.1 or newer.
 * __91__   __*Version mismatch; connecting program uses licensing library '<version>' while TLS requires at least '<version>'*__
   The license server requires that TLS encryption is used when connecting, but the connecting program does not support this feature. Ensure that your application is using Xpress version 9.2.1 or newer.
 * __93__   __*TLS is required by the server but the client did not request a TLS session*__
   The license server requires that TLS encryption is used when connecting, but the connecting program could not load the OpenSSL libraries. Check that the OpenSSL DLLs \(see  _Creating FICO Xpress Runtime Distributions_\) are in the same directory as the other Xpress DLLs.
 * __94__   __*TLS is required but OpenSSL is not available on the server*__
   The license file requires that TLS encryption is used when connecting to the license server, but the license server could not load the OpenSSL libraries. Ensure that the OpenSSL DLLs \(see  _Creating FICO Xpress Runtime Distributions_\) are in the same directory as the license server application, `xpserver`.
 * __95__   __*TLS is required but OpenSSL is not available on the client*__
   The license file requires that TLS encryption is used when connecting to the license server, but the connecting program could not load the OpenSSL libraries. Check that the OpenSSL DLLs \(see  _Creating FICO Xpress Runtime Distributions_\) are in the same directory as the other Xpress DLLs.
 * __103__   __*Your license does not allow Xpress to be run on a Terminal Services server*__
   You can only use Xpress on a Terminal Services server with a Workstation or Server license. If you require a license upgrade, please contact your supplier.
 * __259__   __*This is an OEM license and you have incorrectly specified the OEM number.*__
   You have either called an initialization function without first calling the OEM licensing function or you specified the wrong OEM number in your call to the licensing function. Check your OEM documentation to be sure that you are using the correct initialization sequence. Note that OEM numbers issued for releases earlier than Xpress-MP 2003 are invalid with Xpress-MP 2003 and beyond. If in any doubt, confirm your OEM number with FICO Support.
 * __10006__   __*Invalid JSON type*__
   Web licensing configuration file contains an invalid JSON type.
 * __10007__   __*Invalid JSON format*__
   Web licensing configuration file contains a JSON syntax error.
 * __10008__   __*Cannot initialize licensing with given authentication string*__
   Web licensing configuration file contains invalid credentials. Make sure you have generated Oauth2 'client\_id' and 'client\_secret' for this license and that they are still valid.
 * __10010__   __*No license key found in the config file*__
   Web licensing configuration file is missing the license key. License key is required to activate or use a license.
 * __10011__   __*Given key is not a licensing key*__
   Web licensing configuration file contains a key that is not recognized as a license key. A license key with format 'AAAA-BBBB-CCCC-DDDD' is expected.
 * __10012__   __*Given custom field contains whitespaces or quotes*__
   Your license contains an ill-formatted custom field name. Please contact FICO Support to fix this license.
 * __10013__   __*Given custom field value cannot be parsed*__
   Your license contains an ill-formatted custom field value. Please contact FICO Support to fix this license.
 * __10016__   __*Invalid server type \(should be 'prod' or 'floating'\)*__
   Invalid value for _server_type_ in web licensing configuration file, value should be _prod_ or _floating_.
 * __10104__   __*Invalid configuration settings*__
   Could not initialize licensing with the given web licensing configuration file. Make sure you have correct credentials and the configuration file follows JSON format.
 * __10105__   __*License not found*__
   License key given in web configuration file does not exist.
 * __10106__   __*License has expired*__
   This license has expired, please contact FICO Support to extend validity.
 * __10107__   __*License is disabled*__
   This license is disabled. Please contact FICO Support to enable this license.
 * __10108__   __*Your license is inactive*__
   This license is inactive. Please contact FICO Support to activate this license.
 * __10111__   __*Device from which the call is made is not licensed \(Hardware ID mismatch\)*__
   The license has been issued for a different hardware ID
 * __10114__   __*Could not connect to the server*__
   Unable to connect to the licensing service, please try again.
 * __10115__   __*Request to the backend has timed out*__
   Connection to licensing server has timed out, please try again.
 * __10117__   __*License product code doesn't correspond to configuration product code*__
   License in the web configuration file is not an Xpress Solver license.
 * __10118__   __*Server signature is not valid*__
   Could not validate licensing server signature.
 * __10119__   __*SDK could not read or write license to the storage*__
   Unable to load license from local storage. Please conrtact FICO Support.
 * __10126__   __*The license has already been activated the maximum number of times*__
   Cannot activate the license, it has already been activated the maximum number of times.
 * __10128__   __*Reached max users count for floating license*__
   Cannot use this floating license, it has already reached its maximum amount of simultaneous users.
 * __10130__   __*Device has been added to the blacklist by admin on LicenseSpring platform*__
   This device is not allowed to use web licensing, please contact FICO Support.

### Section 2.7 Dongle Licenses \(for Microsoft Windows Machines\)


Under Windows, licenses are available that are locked to a dongle rather than to the host ID or Ethernet address of the computer. A license file is still required; it will contain the four-digit dongle number in place of the computer's host ID or Ethernet address. The dongle is used only to provide a unique four-digit dongle number to which the license file is locked. The license is only valid when run on the machine to which the dongle is currently attached. All license details, including the Xpress features authorized, whether the license is static or floating, the release of Xpress authorized, and so forth, are contained in the license file.

#### Displaying the Dongle Number


The dongle number can be obtained by running the Xpress Host ID tool \(see  _Full License_ for more information\). Note that the dongle must be connected to your computer and the dongle device driver must be installed and running \(as described below\).

#### Installing the HASP Dongle Device Driver


When installing Xpress for Windows, the setup program automatically tries to install the appropriate device driver. For the driver to install correctly, you must have Administrative privileges and restart the computer once installation is complete.

To enable the dongle drivers for Windows to be installed manually, use the software located in the `tools\dongle` directory. To install the driver, navigate to the `tools\dongle\sentinelhasp` folder and run the `haspdinst.exe` program with a `-i` flag. For example:

```
haspdinst -i
```


#### Notes for Xpress Release 13 \(and Earlier\) Users with Dongles


Releases of Xpress prior to Xpress-MP 2003 used a different mechanism: the license information was included in the dongle itself, and different types of dongle were supplied depending on whether the license was static or floating. When using your existing dongle with Xpress-MP 2003 or later, all information on the dongle, apart from the four-digit dongle number, is ignored. Since your dongle does not need to be updated to work with 2003 or later, it still supports previous releases of Xpress.

If you have a _NetHASP_ dongle \(red plastic casing\), for use with a floating license, the _NetHASP_ license manager is no longer used, and can be disabled. Floating licenses are now administered by the `xpserver` license manager as described in this document. The _NetHASP_ dongle acts as an ordinary dongle and must be attached to the license server.

### Section 2.8 Dongle Licenses \(for Linux Machines\)


Under x86 32-bit and 64-bit x86 Linux, licenses are available that are locked to a dongle rather than to the host ID or Ethernet address of the computer. A license file is still required: this will contain the four digit dongle number in place of the computer's host ID or Ethernet address.

The dongle is used to provide a unique four-digit dongle number to which the license file is locked. The license is only valid when run on the machine to which the dongle is currently attached. All license details, including the Xpress features authorized, whether the license is static or floating, the release of Xpress authorized, and so forth, are contained in the license file.

#### Displaying the Dongle Number


The dongle number can be obtained by running the Xpress Host ID tool \(see the section  _Full License_\). Note that the dongle must be connected to your computer and the dongle device driver installed and running \(as described below\).

#### Installing the HASP Dongle Device Driver


The dongle driver is not automatically installed when installing Xpress on a Linux machine. In order for your dongle to be recognized, you must download the Linux dongle drivers from the FICO Xpress client download page. You must login with your root account, extract all the files from the `aksusbd-1.16.1-i386.tar.gz` archive within the `Sentinel_LDK_Linux_Run-time-Installer_script.tar` archive and run the `dinst` script which will install the HASP dongle driver daemon. After this, the Xpress software should recognize the dongle you plug in. \(Try running the `xphostid` tool to check this. If it reports a hostid starting with `'di'` then it can see your dongle and the driver is correctly installed.\)

### Section 2.9 Community License


The Community license enables development, modeling, and deployment of the industry leading FICO Xpress Optimization software, free of charge. The solvers included in the Xpress Community License are only limited in problem size. In this edition, the sum of the number of rows \(constraints\) and columns \(variables\) is restricted to 5000 for linear and mixed-integer problems, and is restricted to 200 for quadratic and general nonlinear problems. In addition, the number of nonlinear tokens \(measure of the complexity for nonlinear expressions\) is restricted to 1000, and the number of user functions \(black-box optimization\) is restricted to 1. You can unlock these capabilities by purchasing and installing a full license.

### Section 2.10 Redundant Server Licenses


A redundant server license is a special type of license for use in mission-critical environments. It relies on not one license server but three, of which at least two must be active to authorize Xpress. This way, if one license server machine happens to fail, your applications can still use Xpress using the remaining two servers until the problem is corrected.

To obtain a redundant server license, contact your supplier.

 1. You must install the license server application on all three license server machines. Edit your server license file and ensure that the machine names in the `use_server` lines match with the names of your three license server machines. For example:
```
use_server server="main_server" hostid="mx001731e8216c"
use_server server="backup_server_1" hostid="mx002831e8216d"
use_server server="backup_server_2" hostid="mx0017ff88216e"
```

 Install the same server license file on all three redundant server machines.

 2. In the client license, list the three redundant license servers, marked as redundant license servers, as follows:
```
use_server server="main_server" redundant="1"
use_server server="backup_server_1" redundant="1"
use_server server="backup_server_2" redundant="1"
```

 Xpress will try to connect to each of the redundant license servers in turn, until it successfully establishes a connection with one of them.

Keep in mind that you cannot use Xpress when only one redundant license server is active. Xpress will only license successfully if two or three of the redundant license servers are available.

### Section 2.11 Virtualization


Xpress software supports the most common virtualization technologies including VMWare, Microsoft Virtual PC/Server, App-V, and so forth.

#### Static Licensing


Xpress version 7.0 and later supports static \(node locked\) licensing on virtualized hardware.

USB Dongle licenses are compatible with VMware but are unsupported by Virtual PC and Virtual Server.

#### Floating Licensing


All versions of Xpress support the use of floating licenses with virtualization technologies. However, while the clients can be virtual guest operating systems, the license manager itself must be executed on a non-virtual operating system.

#### Application and Enterprise Licensing


Xpress version 7.0 and later supports application and enterprise licensing on virtualized hardware.

#### Virtualization Recommendation


Virtualization is most commonly deployed in a server environment to consolidate resources. The limitations of dongles described earlier make their use unsuitable for most server installations.

FICO recommends that floating or application/Enterprise licensing be used with virtualization technologies as these configurations provide the most reliable means of complying with the terms and conditions of the client's licensing agreement. The license server can be installed as a service on a host operating system or another real machine, locked to the hardware. Virtual guest operating systems are then able to request licenses as necessary over the local network.

#### Using HASP Dongles with VMware


 1. In order to use dongles from a virtual machine running under VMWare, open your virtual machine's settings and ensure the option **Automatically connect new USB devices to this virtual machine when it has the focus**  is selected, as shown in the following example:
 

![install12.png](Graphic/install12.png)


 
With this option activated, any USB device you plug in _while the virtual machine has the focus_will be connected to the virtual machine, rather than to the host operating system.

 2. You can now install Xpress as normal. Select to use hardware dongles as the licensing key when prompted by the installer. Click in the virtual machine window to ensure it has the focus, and if you plug in your dongle now, it should connect to the operating system and be recognized when you run Xpress.

 3. Should you plug in your dongle when the virtual machine does not have the focus, it will be connected to the host operating system instead. To disconnect it from the host and connect it to the virtual machine, bring up the VM menu from VMware, slide across Removable Devices and USB Devices, and select Aladdin Knowledge Systems USB Device as shown in the following example:
 

![install13.png](Graphic/install13.png)



 4. You will be requested to disconnect the dongle from the host and reattach it to the virtual machine. Click **OK** .
 

![install14.png](Graphic/install14.png)



#### Using HASP Dongles with Microsoft Virtual PC


_**Warning:**  Hardware dongles are not currently supported under Microsoft Virtual PC \(including Microsoft Virtual PC 2007\). In addition, it is important that you do not try to install the HASP dongle drivers on a virtual machine hosted by Virtual PC as it has been observed that this can damage the virtual machine, in extreme situations leading to it becoming unbootable. When the Xpress installer prompts you whether to use hardware dongles for licensing, answer **No** ._

#### Using HASP Dongles with Microsoft Virtual Server


Microsoft Virtual Server currently does not support any USB devices, including dongles, except for keyboards& mice. It is not possible to use Xpress with a dongle license through Microsoft Virtual Server.

## Chapter 3 Supported Platforms


### Section 3.1 Operating System and Hardware


The following are the supported platform, operating system, and processor combinations for FICO Xpress \(unless stated otherwise in the following sections for specific components\):


__Platform__ | __Operating System__ | __Processor__ | 
---------- |  ---------- | ---------- | 
Windows 64-bit; | Windows 11; Windows Server 2019; Windows Server 2022; | Any AMD64 or Intel EM64T; enabled 64-bit CPU; | 
Linux 64-bit \(x64\); | RHEL 8; RHEL 9; Ubuntu 22.04 \(Jammy Jellyfish\); Ubuntu 24.04 \(Noble Numbat\); Amazon Linux 2023; | Any AMD64 or Intel EM64T; enabled 64-bit CPU; | 
Linux 64-bit \(aarch64\); | Amazon Linux 2; | ARMv8-A; \(such as Graviton2 on AWS\); | 
macOS 64-bit \(aarch64\); | 14 \(Sonoma\); | Apple Silicon M-series; | 

#### Xpress Solver - Xpress Optimizer, Xpress NonLinear and Xpress Global


Xpress Solver is the framework that supports all of FICO's optimization solver technologies, including Xpress Optimizer, Xpress NonLinear and Xpress Global.

These can be used within our modeling language Xpress Mosel or directly from Python.

 On Linux platforms, the minimum required version of the _glibc_ library is 2.28.

Please refer to the installation instructions in Section  _Prerequisites for Linux Installations_ for dependencies needed for Linux distributions for running the Console Optimizer.

The use of key-based licences \(see Section  _Using Key-based (Static or Web Floating) Licenses_\) requires a C++ runtime distribution, the minimum required version is 14. In the absence of a suitable C++ version, the file-based licensing method needs to be used.

##### Python Support


Xpress Solver can be used with the following Python versions.


__Platform__ | __Python Support__ | 
---------- |  ---------- | 
Windows 64-bit; Linux 64-bit \(x64 and aarch64\); macOS 64-bit \(aarch64\); | Python 3.10; Python 3.11; Python 3.12; Python 3.13; Python 3.14; | 

##### R support


The R interface for Xpress Optimizer can be used with R versions 4.0 and newer on macOS and Linux. The precompiled R-package for Windows supports R version 4.0.

##### Xpress Insight Compute Interface support


The Xpress Optimizer libraries can be configured to interact with a remote Insight server. This is supported on all platforms listed above \(Section  _Operating System and Hardware_\).

In addition, access to an Xpress Insight 5 server is required \(see the [_Insight 5 Installation Guide_](https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/install), and in particular the chapter [Supported Platforms](https://www.fico.com/fico-xpress-optimization/docs/latest/insight5/install/GUID-D57B213B-3AEA-4B8A-9027-128B5B7D8A7F.html)\).

##### GPU support for PDHG \(beta release\)


The primal-dual hybrid gradient \(PDHG\) linear optimization solver using a NVIDIA® CUDA® -capable GPU has been tested on the following operating systems and platforms:


__Platform__ | __Operating System__ | 
---------- |  ---------- | 
Windows 64-bit; | Windows 11; Windows Server 2022; | 
Linux 64-bit \(x64\); | RHEL 9; Ubuntu 22.04 \(Jammy Jellyfish\); Ubuntu 24.04 \(Noble Numbat\); Amazon Linux 2023; | 
Linux 64-bit \(aarch64\); | Amazon Linux 2023; | 

**Hardware requirements:** 

 * 
NVIDIA GPU with microarchitecture Turing, Ampere, Ada Lovelace, Hopper or Blackwell.


Please refer to the installation instructions in Section  _GPU installation guidelines for PDHG_ for additional software and driver requirements.

#### Xpress Mosel


The Xpress Mosel language allows the user to define his models in a form that is close to algebraic notation and to solve them in the same environment.

It interfaces to statistics packages such as R or Matlab. Mosel provides a module _python3.dso_ that implements functionality for exchanging data between a Mosel model and Python 3 \(C Python\) and for calling Python 3 scripts.

 * Xpress Workbench is the premier choice as IDE \(Integrated Development Environment\) for standalone Mosel models and Xpress Insight apps. It integrates with Insight for remote debugging. Xpress Workbench is available for Windows and macOS as part of the Xpress installer, and as part of [Docker images](https://www.fico.com/fico-xpress-optimization/docs/latest/dockerGuide).

##### Python Support


Mosel provides a module _python3.dso_ that implements functionality for exchanging data between a Mosel model and Python 3 \(CPython\) and for calling Python 3 scripts. The Mosel run-time library loads and runs the Python interpreter. Xpress Mosel can be used with the following Python versions:
 * Python 3.10 to Python 3.14


The Python package _moselpy_ for embedding Mosel models into Python programs supports the same Python versions as the Mosel module.

##### R support


The R interface for Xpress Mosel makes it possible to easily exchange data with R and execute R scripts, or evaluate expressions in the R language, from within a Mosel model.
 * Mosel supports R versions 4.0 to 4.1.x


**Note:**  Download the version of R from the R Project web site at [www.r-project.org](HTTP://WWW.R-PROJECT.html), targeting the same platform as Mosel. Therefore, if you have Windows 64-bit Mosel installed, download a matching R version.

##### Data Sources


Mosel can connect to data in memory through files, databases and web services. It connects to any ODBC-enabled data source, has a specific Oracle driver and drivers for Excel, CSV, XML, JSON as well as its own DAT format. Users can implement custom drivers and use Mosel's free form reading and writing capabilities.

#### Xpress Solver - Xpress Kalis


Xpress Kalis provides access to the Artelys Kalis Constraint Programming \(CP\) solver from a Mosel module allowing the user to formulate and solve CP models in the Mosel language.

Xpress Kalis combines a finite domain solver and a solver over continuous \(floating point\) variables. All data handling facilities of the Mosel environment, including data transfer in memory and ODBC access to databases can be used with Xpress Kalis.


__Platform__ | __Operating System__ | __Processor__ | 
---------- |  ---------- | ---------- | 
Windows 64-bit; | Windows 11; Windows Server 2019; Windows Server 2022; | Any AMD64 or Intel EM64T; enabled 64-bit CPU; | 
Linux 64-bit; | RHEL 8 or later; | Any AMD64 or Intel EM64T; enabled 64-bit CPU; | 

#### Xpress Solver - Knitro


Xpress Knitro is a nonlinear solver provided by Artelys. It is accessible through Xpress Solver and is supported on the same platforms \(see Section  _Operating System and Hardware_\).

### Section 3.2 Interfaces


#### Java


The interfaces for calling Xpress libraries from Java require a minimum of Java 8 \(internal version: 1.8.0\); compatible distributions of Oracle Java and OpenJDK are supported.

The Mosel module _mosjvm_ works with Java 8, 11 and 17. Java 8 is not available on macOS ARM. The module is tested on Amazon Corretto.

#### .NET


The interfaces for calling Xpress Solver and Mosel libraries from .NET are available for Windows and Linux platforms, and require .NET 8.

#### C++


The interface for calling Xpress Solver from C++ requires a minimum of C++ 17.

## Chapter 4 Creating FICO Xpress Runtime Distributions


For distributing an application that uses some portion ofFICO Xpress Optimization to end-users we recommend that you distribute the whole installation package, but if you only want to distribute parts of it then here is how to do it.

### Runtime Libraries and Other Dependencies


 1. Make sure that there is no other Xpress software, library files or license files on the path or in any directories used or accessed by your application– in particular, be careful that no earlier releases of Xpress software are present.
 2. The files you need to _run_ \(but not _compile_\) applications depend on which of the Xpress libraries you are using. Here we give the files required for Windows and Linux; the files required for other Unix operating systems are similar to those required for Linux, but the exact file names sometimes differ in an obvious way. \(The suffix X in Linux file names indicates the version number.\) All of these files \(with the exception of your particular license file, `xpauth.xpr`\) should be taken from the current Xpress release distribution. See note 9 below for an explanation of the UNIX symbolic links required for UNIX installations.
     * An **Optimizer application**  requires the files

|  | __Windows__ | __Linux__ | __Notes__ | 
---------- |  ---------- | ---------- | ---------- | 
_Optimizer library_ | `xprs.dll` | `libxprs.so.*` | 
_Optimizer library Java wrapper_ | `javaxprs.dll` | `libjavaxprs.so` | \(Java and MATLAB Java only\) | 
_Xpress support library_ | `xprl.dll xpnll.dll` | `libxprl.* libxpnll.*` |  | 
_MATLAB interface_ | `xprs*.mexw*` | `xprs*.mex*` | \(MATLAB only\) | 
_Knitro library_ | `xknitro.dll xknitronl.dll libiomp5md.dll` | `libxknitro.so.* libxknitronl.so.*` | \(if required\) | 
_License file_ | `xpauth.xpr` | `xpauth.xpr` |  | 

   *  
 * For a Python application, the `xpress` package from Pip or Anaconda must be installed in the Python environment containing your application. Please refer to the Python interface reference manual for installation instructions.
 * For an R application, the `xpress` package must be installed in the R environment containing your application. Instructions for installing this package can be found in the `R/INSTALL.txt` file in your Xpress installation.
 * For a .NET application, you would require either the `FICO.Xpress.XPRSdn.*.nupkg` package or the `xprsdn.dll` file from within it, depending upon how you distribute your application. NuGet packages for Xpress are not available through online package repositories. Xpress .NET libraries can be used on Windows and Linux platforms only.


An application outsourcing optimization solves to the **Xpress Insight Compute Interface**  requires additional files

| &nbsp; | &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | ---------- | 
_Optimizer Webservices client library_ | `xprsws.dll` | `libxprsws.so.*` |  | 
_Curl library_ | `libcurl.dll` | `libcurl.so.*` |  | 
_Jansson library_ | `jansson.dll` | `libjansson.so.*` |  | 
_Libwebsockets library_ | `websockets.dll` | `libwebsockets.so.*` |  | 
_OpenSSL libraries_ | `libcrypto*.dll` `libssl*.dll` | `libcrypto.so.*` `libssl.so.*` |  | 
_Zip library_ | `libzip.dll` | `liblibzip.so.*` |  | 


A **Mosel \(run-time library\) application**  requires the files

| &nbsp; | &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | ---------- | 
_Optimizer library_ | `xprs.dll` | `libxprs.so.*` | \(if required, see additional dependencies below\) | 
_Mosel library_ | `xprm_rt.dll` | `libxprm_rt.so.*` |  | 
_Mosel executable_ | `mosel.exe` | `mosel` | \(required for remote connections or Mosel command line\) | 
_Mosel library Java wrapper_ | `xprm_rtJ.dll` | `libxprm_rtJ.so.*` | \(Java and MATLAB Java only\) | 
_Mosel compiler library_ | `xprm_mc.dll` | `libxprm_mc.so.*` | \(if required, _e.g._ by executable\) | 
_Mosel compiler library Java wrapper_ | `xprm_mcJ.dll` | `libxprm_mcJ.so.*` | \(Java only; if required\) | 
_Mosel library .NET wrapper helper DLL_ | `xprndn-c-` `helper.dll` | `libxprndn-c-` `helper.so` | \(Windows/Linux .NET only\) | 
_MATLAB interface_ | `moselexec.mexw*` | `moselexec.mex*` | \(MATLAB only\) | 
_Natural language support_ | `xprnls.dll` | `libxprnls.so` |  | 
_Mosel modules or packages used_ | `XXX.dso` `XXX.bim` | `XXX.dso` `XXX.bim` | \(as required, see additional dependencies below\) | 
_VB library extensions_ | `xprmvb.dll` | N/A | \(VB only\) | 
_Xpress support library_ | `xprl.dll xpnll.dll` | `libxprl.* libxpnll.*` | 
_License file_ | `xpauth.xpr` | `xpauth.xpr` |  | 


     * For a .NET application, you would require either the `FICO.Xpress.XPRMdn.*.nupkg` package or the `xprmdn.dll` file from within it, depending upon how you distribute your application. NuGet packages for Xpress are not available through online package repositories. Xpress .NET libraries can be used on Windows and Linux platforms only.

Certain **Mosel modules or packages**  have **additional dependencies** , so these files also need to be provided if you use the specified component:

| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_aec2.bim_ | `mmjobs.dso mmhttp.dso mmssl.dso` |  | 
|  | `mmsystem.dso mmxml.dso` |  | 
|  | Windows: `mplink.exe mpscp.exe` |  | 
_dmp.dso_ | `mmhttp.dso mmsystem.dso` |  | 
|  | Windows: `jansson.dll` | 
|  | Unix: `libjansson.so.*` |  | 


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_executor.bim_ | `mmjobs.dso mmhttp.dso mmxml.dso` | 
|  | `mmsystem.dso executor.dso` | 
|  | Windows: `jansson.dll` | 
|  | Unix: `libjansson.so.*` |  | 
_fssappstudio.bim_ | `mmxml.dso mmsystem.dso` |  | 
_kalis.dso_ | Windows: `Kalis.dll xprs.dll` | \(Windows and Linux\) | 
|  | Linux: `libKalis.so libxprs.so.*` | 
|  | `libstdc++.so.* libgcc_s.so.*+` | 
_matlab.dso_ | \(MATLAB installation required\) | 


| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_mmhttp.dso_ | `mmjobs.dso mmsystem.dso` |  | 
_mminsight.bim_ | `mminsight.dso mmxprs.dso mmxml.dso` | \(extract Xpress Insight Developer Kit to Xpress installation directory\) | 
|  | `mmsystem.dso mmhttp.dso mmjobs.dso` | 
|  | `trusteddsn.dso mmssl.dso` | 
|  | `s3.dso s3.bim debugarchive.bim` | 
|  | `mminsightannotations.bim` |  | 
_mmjobs.dso_ | Windows: `xprm_mc.dll` | 
|  | Unix: `libxprm_mc.so.*` |  | 
_mmoci.dso_ | \(Oracle Instant Client installation required\) | 
_mmrobust.dso_ | `mmxprs.dso` | 
|  | Windows: `xprs.dll`/ Unix: `libxprs.so.*` |  | 


| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_mmsheet.dso_ | Windows: `libxl.dll` | \(Windows, Linux, OSX\) | 
_mmssl.dso_ | `mmsystem.dso` | 
|  | Windows: `LIBEAY32.dll SSLEAY32.dll` | 
|  | Unix: `libssl.so.* libcrypto.so.*` |  | 
_mmsvg.bim_ | `mmsystem.dso mmjobs.dso` | 
|  | `mmxml.dso mmsvg.tgz` |  | 
_mmxml.dso_ | `mmsystem.dso` |  | 


| &nbsp; | &nbsp; | 
---------- |  ---------- | 
_mmxnlp.bim_ | `mmxprs.dso mmnl.dso mmjobs.dso` | 
|  | `mmsystem.dso mmxnlp.dso` | 
|  | Windows: `xprs.dll`/ Unix: `libxprs.so.*` |  | 
|  | Knitro solver \(optional\): | 
|  | Windows: `xknitro.dll xknitronl.dll` | 
|  | `libiomp5md.dll` | 
|  | Unix: `libxknitro.so.* libxknitronl.so.*` | 


| &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | 
_mmxprs.dso_ | Windows: `xprs.dll`/ Unix: `libxprs.so.*` |  | 
_python3.dso_ | \(Python 3 installation required\) | 
_r.dso_ | \(R installation required\) | 
_s3.bim_ | `mmjobs.dso mmssl.dso mmxml.dso` | 
|  | `mmsystem.dso mmhttp.dso s3.dso` | 
|  | Windows: `jansson.dll` | 
|  | Unix: `libjansson.so.*` |  | 
_zlib.dso_ | Unix: `libz.so.*` | \(no extra dependency on Windows\) | 
_mmssl executable_ | Windows: `mmssl.exe`/ Unix: `mmssl` | \(required for https setup\) | 
_xprmsrv executable_ | Windows: `LIBEAY32.dll ssh.dll` | 
|  | Unix: `libssh.so.* libcrypto.so.*` | \(for remote connections\) | 


If you are using a **floating license** , you also need these files:

| &nbsp; | &nbsp; | &nbsp; | &nbsp; | 
---------- |  ---------- | ---------- | ---------- | 
_Xpress license manager_ | `xpserver.exe` | `xpserver` |  | 
_License state query tool_ | `xplicstat.exe` | `xplicstat` |  | 
_OpenSSL libraries_ | `libcrypto*.dll` `libssl*.dll` | `libcrypto.so.*` `libssl.so.*` |  | 


     * Some of the components ofFICO Xpress Optimization contain open source software. When redistributing parts of Xpress please make sure that you also include the corresponding files from the `licenses` subdirectory of the Xpress distribution.

 3. Copy all of the Xpress files listed above to one directory on your end-user's computer. This can be any directory, but we strongly recommend that you use the directory containing your application program.
   *  If you are building a runtime distribution for **Mosel** applications we recommend that you maintain the same subdirectory structure \(with directories `bin`, `dso`, `lib`, and if you are using MATLAB also `matlab`\) as the original Xpress distribution.

 4. **Windows**  libraries: Add the directory containing the Xpress files to the Windows `PATH`, so that Windows knows where to find the Xpress DLLs.

 5. **Unix**  libraries: Add the directory containing the Xpress libraries to the environment variable for locating shared libraries on your platform \( `LD_LIBRARY_PATH` for Linux, `DYLD_LIBRARY_PATH` on macOS\).

 6. **Windows**  licensing: Copy the Xpress license file, `xpauth.xpr`, into the directory containing the Xpress DLLs. If you store the license file in a different location, set the `XPAUTH_PATH` environment variable to its full path. It is not recommended to store the license file in a different location, because it adds to the complexity of the Xpress licensing procedure and makes it difficult to support your application on your end-user's computer. For the same reason, it is not recommended to specify the location of the license file by passing an explicit path argument \(to `XPR?license` or `XPR?init`\) when initializing Xpress.

 7. **Unix**  licensing: Set the environment variable `XPAUTH_PATH` to the full path to the Xpress license file, `xpauth.xpr`.
_**Note:**  Previous releases of Xpress used the `XPRESS` environment variable to locate the license file. This is now deprecated in favour of the `XPAUTH_PATH` environment variable. When upgrading, please ensure that any installation scripts, application code and documentation is updated to use `XPAUTH_PATH` instead of `XPRESS`._


 8. If you are using **Mosel** , set the environment variable `MOSEL_DSO` to point to the directory containing the Mosel DSO files.

 9. **Unix**  symbolic links: The tar file distributions contain symbolic links  _e.g._  `libxprs.so.17.10.01 ->  libxprs.so.17.10 ->  libxprs.so` \( `.so` extension may vary between UNIX platforms\).
   *  In the example above, the binary file has the full version number postfixed to enable the support team to easily identify the exact version number being used. The intermediate filename without the 3<sup>rd</sup>element of the version number is used internally by one Xpress component to link to another. The link with no version number is used to support the version-independent documentation, examples and example makefiles.
   *  In general,it is possible to remove the soft links and rename the libraries, with the following exceptions. The security library must be made available as libxprl.so. _yyyy_for all Xpress components to use. If any components \( including Xpress Optimizer console \) other than the Xpress Optimizer runtime library are to be used then the Xpress Optimizer runtime library must be made available as libxprs.so. _xx.yy_.

### Dongles


 11. If you are using Xpress dongles, you must install the dongle driver on your end-user's computer. You can obtain the files necessary to do this from the fico.com website:
     * For **HASP**  dongles on **Windows** , you need the file
```
\windows\dongle\hasp\hinstall.exe
```

 Administrator privileges are required to install the dongle driver. To install the driver, execute
```
hinstall -i -criticalmsg
```

 The driver does not normally start up until the computer is re-booted.

     * For **HASP**  dongles on **Linux**  you need the file `HDD_Linux_dinst.tar.gz` \(available from the Xpress client area download page\); to install the dongle driver daemon you must uncompress this archive somewhere convenient, switch to your superuser account and run the supplied `dinst` shell script.


### Floating Licenses


 12. Users with floating licenses: make sure the Xpress license manager is installed and running on the server machine. Please refer to the chapter  _FICO Xpress Licensing_ for full instructions and troubleshooting. If you wish to install the license server as a service on Windows machines, run this command:
```
xpserver -service install
```

 and to remove the service:
```
xpserver -service remove
```



 13. Users with floating licenses: when creating your installer for the client machines you will have to construct an `xpauth.xpr` file for connecting to the server. This file should contain one line as follows:
```
use_server name="<servername>"
```

 Where `< servername>` is the name of the license server machine. You may wish to prompt the user for this information as part of the install process.
