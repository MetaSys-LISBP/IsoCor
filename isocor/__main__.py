import isocor.ui.isoCorGUI
import isocor.ui.isoCorCli
import sys

# start CLI if arguments provided, otherwise switch to GUI
if len(sys.argv) > 1:
    isocor.ui.isoCorCli.startCli()
else:
    isocor.ui.isoCorGUI.startGUI()
