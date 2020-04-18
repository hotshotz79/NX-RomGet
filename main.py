import imgui
import imguihelper
import os
import _nx
import runpy
import sys
from imgui.integrations.nx import NXRenderer
from nx.utils import clear_terminal
import time
import urllib.request
import urllib.parse
import zipfile

sys.argv = [""]  # workaround needed for runpy

def colorToFloat(t):
    nt = ()
    for v in t:
        nt += ((1/255) * v, )
    return nt

# (r, g, b)
FOLDER_COLOR = colorToFloat((230, 126, 34))
PYFILE_COLOR = colorToFloat((46, 204, 113))
FILE_COLOR = colorToFloat((41, 128, 185))
C_RED = (0.9, 0.0, 0.1)
C_ORANGE = (0.9, 0.4, 0.0)
C_YELLOW = (0.8, 0.9, 0.0)
C_LIME = (0.5, 0.9, 0.0)
C_GREEN = (0.0, 0.9, 0.2)
C_AQUA = (0.0, 0.9, 0.6)
C_BLUE = (0.0, 0.5, 0.9)
C_NAVY = (0.2, 0.0, 0.9)
C_PURPLE = (0.6, 0.0, 0.9)
C_PINK = (0.9, 0.0, 0.8)

TILED_DOUBLE = 1

# Progress Bar---------------------------------------
def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r...%d%%, %d / %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), total_size / (1024 * 1024), speed, duration))
    #sys.stdout.write("\rPercent: %d%% | Downloaded: %d of %d MB | Speed: %d KB/s | Elapsed Time: %d seconds" %
    #                (percent, progress_size / (1024 * 1024), total_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

# Start Download-------------------------------------
def start(filename, url, consolefolder, extract):
    # clear both buffers
    imguihelper.clear()
    _nx.gfx_set_mode(TILED_DOUBLE)
    clear_terminal()
    
    # filename = urllib.parse.unquote(url.split('/')[-1])
    zippath = filename + ".zip"
    print("-------------------------------------------------------------------------------")
    print("\n            _   _ __   __     ______                _____      _   " +
            "\n           | \ | |\ \ / /     | ___ \              |  __ \    | |  " +
            "\n           |  \| | \ V /______| |_/ /___  _ __ ___ | |  \/ ___| |_ " +
            "\n           | . ` | /   \______|    // _ \| '_ ` _ \| | __ / _ \ __|" +
            "\n           | |\  |/ /^\ \     | |\ \ (_) | | | | | | |_\ \  __/ |_ " +
            "\n           \_| \_/\/   \/     \_| \_\___/|_| |_| |_|\____/\___|\__|")
    print("\n-------------------------------------------------------------------------------\n")
    print("\n[Rom Selected]  " + filename)
    print("\n[Download Path] sdmc:/Roms/" + consolefolder + "/")
    print("\n-------------------------------------------------------------------------------\n")
    print("Download Progress:\n")
    urllib.request.urlretrieve(url, "sdmc:/Roms/" + consolefolder + "/" + zippath, reporthook)
    print("\n\n File Downloaded")
    
    # Extraction Section
    if extract:
        print("\n-------------------------------------------------------------------------------\n")
        print("\n[Extraction Path] sdmc:/Roms/" + consolefolder + "/" + filename + "/")
        print("Extraction Progress:\n")
        path_to_extract = "sdmc:/Roms/" + consolefolder + "/" + filename
        zf = zipfile.ZipFile("sdmc:/Roms/" + consolefolder + "/" + zippath)
        uncompress_size = sum((file.file_size for file in zf.infolist()))
        extracted_size = 0

        i = len(zf.infolist())
        x = 1

        for file in zf.infolist():
            extracted_size += file.file_size
            print("Extracting " + str(x) + " of " + str(i) + ": " + file.filename + " | Size: " + str(file.file_size / 1000000)[0:5] + " MB | Progress: " + str((extracted_size * 100/uncompress_size))[0:3] + "%")
            zf.extractall(path_to_extract)
            x += 1

    imguihelper.initialize()

# DISPLAY ROMS---------------------------------------
def romList(console_selected):
    # clear both buffers
    imguihelper.clear()
    _nx.gfx_set_mode(TILED_DOUBLE)
    clear_terminal()
    imguihelper.initialize()
    
    renderer = NXRenderer()
    checkbox_extract = False
    
    while True:
        renderer.handleinputs()

        imgui.new_frame()

        width, height = renderer.io.display_size
        imgui.set_next_window_size(width, height)
        imgui.set_next_window_position(0, 0)
        imgui.begin("",
            flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.set_window_font_scale(1.2)
        imgui.text(console_selected.upper())
        
        # TODO
        # ADD Checkbox for "Extract ZIP" & "Delete ZIP"
        
        # Create Selected Systems Directory
        directory = console_selected
        parent_dir = "sdmc:/Roms"
        path = os.path.join(parent_dir, directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as error:
            print("Directory '%s' can not be created" % directory)
        
        button_number = 0
        imgui.separator()
        imgui.new_line()
        
        # Go Back
        imgui.push_style_color(imgui.COLOR_BUTTON, *FOLDER_COLOR)
        if imgui.button("GO BACK", width=288, height=60):
            main()
        imgui.pop_style_color(1)
        
        # Checkbox for Extracting
        imgui.same_line(spacing=50)
        _, checkbox_extract = imgui.checkbox("EXTRACT .ZIP AFTER DOWNLOAD", checkbox_extract)
                
        imgui.new_line()
        
        imgui.separator()
        
        firstRow = True;
        txtFile = console_selected + ".txt"
        file = open(txtFile,"r")
        
        # Generate button for each record found
        for line in file:
          fields = line.split(";")
          title = fields[0]
          link = fields[1]
          
          if button_number == 4:
            imgui.new_line()
            button_number = 0
          else:
            imgui.same_line()
          
          if firstRow == True:
            imgui.new_line()
            firstRow = False
          
          imgui.push_style_color(imgui.COLOR_BUTTON, *FILE_COLOR)
          if imgui.button(title.upper(), width=288, height=60):
            start(title, link, console_selected, checkbox_extract)
          
          imgui.pop_style_color(1)
          
          button_number += 1

        file.close()

        imgui.end()

        imgui.render()
        renderer.render()

    renderer.shutdown()
    

# MAIN-----------------------------------------------
def main():
    renderer = NXRenderer()
    currentDir = os.getcwd()

    while True:
        renderer.handleinputs()

        imgui.new_frame()

        width, height = renderer.io.display_size
        imgui.set_next_window_size(width, height)
        imgui.set_next_window_position(0, 0)
        imgui.begin("",
            flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SAVED_SETTINGS
        )
        imgui.set_window_font_scale(2.0)
        imgui.text("NX-RomGet (ver 0.1)")
        
        # Create ROMS folder if it doesnt exist
        directory = "Roms"
        parent_dir = "sdmc:/"
        path = os.path.join(parent_dir, directory)
        try:
            os.makedirs(path, exist_ok = True)
        except OSError as error:
            print("Directory '%s' can not be created" % directory)
        
        # ------------- COLORS -------------
        # C_RED | C_ORANGE | C_YELLOW | C_LIME | C_GREEN
        # C_AQUA | C_BLUE | C_NAVY | C_PURPLE |C_PINK
        
        # Check which Console Files exist (.txt)
        console_files = []
        for e in os.listdir():
            if e.endswith(".txt"):
                console_files.append(e.replace(".txt", ""))
        console_files = sorted(console_files)
        
        btn_number = 0
        starting_row = True;
        
        # Generate buttons for each Console File found
        for e in console_files:
        
            if btn_number == 3:
                imgui.new_line()
                btn_number = 0
            else:
                imgui.same_line()
          
            if starting_row == True:
                imgui.new_line()
                starting_row = False
            
            if e.startswith("Nintendo"):
                imgui.push_style_color(imgui.COLOR_BUTTON, *C_RED)
            elif e.startswith("Sega"):
                imgui.push_style_color(imgui.COLOR_BUTTON, *C_NAVY)
            elif e.startswith("Sony"):
                imgui.push_style_color(imgui.COLOR_BUTTON, *C_PURPLE)
            elif e.startswith("Final"):
                imgui.push_style_color(imgui.COLOR_BUTTON, *C_GREEN)
            else:
                imgui.push_style_color(imgui.COLOR_BUTTON, *C_ORANGE)
            if imgui.button(e, width=390, height=150):
                romList(e)          
            imgui.pop_style_color(1)
            
            btn_number += 1
        
        #------------------------------
        
        imgui.end()

        imgui.render()
        renderer.render()

    renderer.shutdown()

if __name__ == "__main__":
    main()
