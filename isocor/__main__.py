import isocor.ui.isocorgui
import isocor.ui.isocorcli
import sys

# start CLI if arguments provided, otherwise switch to GUI
if len(sys.argv) > 1:
    isocor.ui.isocorcli.start_cli()
else:
    isocor.ui.isocorgui.start_gui()
