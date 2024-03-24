#!/usr/bin/env python3

import subprocess
import sys
import os
import time
from pathlib import Path

SCRIPT_TITLE = "Video streamer and audio downloader (vistrad)"
historyFilename = "vistrad-history_-_" + time.strftime("%m-%Y", time.localtime()) + ".md"
global historyFile
historyFile = Path(Path.home() / ".cache/yt-dlp/" / historyFilename)


def videoLog(videoSearch):
    
    # If historyFile is not found, creating one
    if Path(historyFile).exists() == False:
        Path(historyFile).touch(0o755, exist_ok = True)
    
    # Get video title and write it with date and URL to the historyFile
    videoTitle = subprocess.run(["yt-dlp", "--get-title", videoSearch], text = True, capture_output = True).stdout.rstrip("\n")
    with open(historyFile, "a") as file:
        currentDate = time.strftime("%d-%m-%Y---%H:%M:%S", time.localtime())
        videoData = "[" + videoTitle + "](" + videoSearch + ") - " + currentDate + "\n"
        file.write(videoData)


def resolutionOptions():

    videoResolutions = [ "1080", "720", "480" ]
    resolutionOption = subprocess.run(f'yad --list --column="Select the resolution for the video" {videoResolutions} --width=600 --height=400', text = True, shell = True, capture_output = True).stdout.rstrip(",[]|\n").lstrip("[")

    # Check if the resolution choosed by user is on the list, if none is selected, exit script
    if resolutionOption in videoResolutions:
        global mpvResolution
        mpvResolution = f'--ytdl-format="bestvideo[height<=?{resolutionOption}]+bestaudio/best"'
    else:
        subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "No resolution selected or identified. Script closed"], text = True)
        sys.exit(1)


def videoStream(videoSearch):

    allowedLinks = ["https://www.youtube.com/watch?v=", "https://youtube.com/watch?v=", "https://youtu.be/", "https://www.twitch.tv/", "https://twitch.tv/", "https://youtube.com/shorts/", "https://www.youtube.com/shorts/"]

    for link in allowedLinks:
        if link in videoSearch:

            resolutionOptions()
            subprocess.run(["notify-send", SCRIPT_TITLE, "Detected video URL and resolution. Opening on MPV."], text = True)
            videoLog(videoSearch)

            if os.path.exists("/usr/bin/mpv") or os.path.exists("/usr/local/bin/mpv"):
                mpvExec = "mpv"
            elif os.path.exists("/var/lib/flatpak/exports/bin/io.mpv.Mpv") or os.path.exists( Path.home() / ".local/share/flatpak/exports/bin/io.mpv.Mpv"):
                mpvExec = "io.mpv.Mpv"
            else:
                subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "MPV not installed or identified. Script closed."], text = True)
                sys.exit(1)

            subprocess.Popen(f"{mpvExec} {mpvResolution} '{videoSearch}' 2>/dev/null &", text = True, shell = True)
            sys.exit(0)

    else:
        searchForVideo(videoSearch)


#Function to download audio
def audioDownload(videoSearch):
    # Get music directory from XDG standards, if not, check if exists "audio downloads" directory on $HOME, if not, create it
    xdgMusicDir = subprocess.run(["xdg-user-dir", "MUSIC"], text = True, capture_output = True).stdout.rstrip("\n")
    
    # If the xdgMusicDir not exists, then create an alternative directory for the audio files
    if Path(xdgMusicDir).is_dir() == False:
        xdgMusicDir = Path.home() / "audio downloads"
        subprocess.run(["notify-send", SCRIPT_TITLE, f"Music folder not found. Making\n{xdgMusicDir}"], text = True)
        Path.mkdir(xdgMusicDir, 0o755, exist_ok = True)
    
    os.chdir(xdgMusicDir)

    # Asks user about bitrate
    answerAudioQuality = subprocess.run(["yad", "--list", "--column=Do you want the best audio quality available?", "no","yes", "--width=600", "--height=400"], text = True, capture_output = True).stdout.rstrip("|\n")

    if answerAudioQuality == "no":
        # Downloading default quality audio
        subprocess.run("yt-dlp -x --audio-format opus " + videoSearch + " --postprocessor-args '-c:a libopus -b:a 96K'", text = True, shell = True)
        subprocess.run(["notify-send", SCRIPT_TITLE, "Download and conversion completed without errors"], text = True)

    elif answerAudioQuality == "yes":
        # Downloading best quality audio
        subprocess.run("yt-dlp -x --audio-format opus " + videoSearch, text = True, shell = True)
        subprocess.run(["notify-send", SCRIPT_TITLE, "Download and conversion completed without errors"], text = True)

    else:
        subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "No audio quality selected or identified. Script closed"], text = True)
        sys.exit(1)


def searchForVideo(videoSearch):

    subprocess.run(["notify-send", SCRIPT_TITLE, "Searching your video. Wait a few seconds"], text = True)

    searchResults = subprocess.run(["yt-dlp", "--get-id", "--get-title", "--flat-playlist", "ytsearch80:" + videoSearch], text = True, capture_output = True).stdout
    
    # Making a file and write the search results in it
    searchResultsFile = Path(Path.home() / ".cache/yt-dlp" / "searchResults.txt")
    
    if searchResultsFile.is_file() == False:
        searchResultsFile.touch(0o755, exist_ok = True)

    # Write the search results overwriting if there are existing ones
    with open(searchResultsFile, "w") as file:
        file.write(searchResults)


    fileLines = open(searchResultsFile, "r").readlines()

    line_number = 0
    searchResults = []
    separator = " ((###)) "
    for line in fileLines:
        if line_number % 2 == 0:

            lineContent = fileLines[line_number].rstrip("\n")
            nextLineContent = fileLines[line_number + 1].rstrip("\n")
            
            resultJoin = lineContent + separator + nextLineContent

            searchResults.append(resultJoin)
            searchResults.sort()
        line_number += 1


    # Show video results on a list to the user select one and strip the last characters inserted by Yad
    selectedVideo = subprocess.run(f'yad --list --column="Search results for: {videoSearch}" {searchResults} --width=800 --height=600', text = True, shell = True, capture_output = True).stdout.rstrip(",|\n")

    # check if selectedVideo is empty
    if selectedVideo == "":
        subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "Video not selected. Leaving"], text = True)
        sys.exit(1)

    videoTitle = selectedVideo.split(separator, 1)[0]
    videoID = selectedVideo.split(separator, 1)[1]
    
    subprocess.run(["notify-send", SCRIPT_TITLE, f"Video to be played: {videoTitle}"], text = True)
    
    # Put before the video ID the Youtube URL
    videoSearch = f"https://youtu.be/{videoID}"

    # Removing the searchResultsFile and changing directory to $HOME
    Path.unlink(searchResultsFile)
    os.chdir(Path.home())

    videoStream(videoSearch)



def main():

    historyAsk = subprocess.run(["yad", "--list", "--column=Do you want to see the video history?", "No", "Yes", "--width=600", "--height=400"], text = True, capture_output = True).stdout.rstrip("|\n")

    if historyAsk == "Yes":
        subprocess.run(f"com.raggesilver.BlackBox --command='xdg-open {historyFile}' &", text = True, shell = True)


    videoSearch = subprocess.run(["yad", "--entry", "--text", "Type your search:", "--width=480", "--height=150"], text = True, capture_output = True).stdout.rstrip("\n")

    if videoSearch == "":
        subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "Search or URL not detected. Leaving"], text = True)
        sys.exit(1)


    ytCacheDir = Path.home() / ".cache/yt-dlp"

    if Path(ytCacheDir).is_dir() == False:
        Path.mkdir(ytCacheDir, 0o755, exist_ok = True)
        
    os.chdir(ytCacheDir)


    mediaWantedAnswer = subprocess.run(["yad", "--list", "--column=Do you want to stream videos or download audio?", "Stream video", "Download audio", "--width=600", "--height=400"], text = True, capture_output = True).stdout.rstrip("|\n")

    if mediaWantedAnswer == "Stream video":
        videoStream(videoSearch)
        sys.exit(0)
    elif mediaWantedAnswer == "Download audio":
        audioDownload(videoSearch)
        sys.exit(0)
    else:
        subprocess.run(["notify-send", "-u", "critical", SCRIPT_TITLE, "No option selected. Leaving"], text = True)



# If the script is executed directly from commandline and not imported as a module, execute the main() function
if __name__ == "__main__":
    main()
