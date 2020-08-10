#!/usr/bin/env bash
## 'status_display_program' for Cmus. Shows album art in a fixed size window.
## Use your window manager to automatically manipulate the window.
## There are several album art viewers for Cmus but this I believe is the most
## compatible with different setups as it is simpler. No weird hacks.

## Requires feh (light no-gui image viewer).
# Uncomment the next line to disable..........
# exit

FOLDER=$( cmus-remote -Q | grep "file" | sed "s/file //" | rev | \
cut -d"/" -f2- | rev )

FLIST=$( find "$FOLDER" -maxdepth 1 -type f )

if echo "$FLIST" | grep -i ".jpeg\|.png\|.jpg" &>/dev/null; then
	ART=$( echo "$FLIST" | grep -i "Wallpaper.png\|Wallpaper.jpg\|cover.jpg\|cover.png\|front.jpg\|front.png\
	\|folder.jpg\|folder.png\|downloaded_cover.jpg\|downloaded_cover.png" | head -n1 )
	echo $FLIST
	
	# If null string try for any png
	if [[ -z "$ART" ]]; then
		ART=$( echo "$FLIST" | grep -i ".png\|.jpg\|.jpeg" | head -n1 )
	fi

	if [[ -z "$ART" ]]; then
		ART=$( /home/yid/programming/downloader/thumb.py )
	fi

	PROC=$( ps -eF | grep "feh" | grep -v "cmus\|grep" | cut -d"/"  -f2- )
	
	if [[ "/$PROC" == "$ART" ]]; then
		exit
	fi
	
	killall -q feh
	
	# '200x200' is the window size for the artwork. '+1160+546' is the offset.
	# For example, if you want a 250 by 250 window on the bottom right hand corner of a 1920 by 1080 screen: "250x250+1670+830"
#	setsid feh -g 200x200+1160+546 -x --zoom fill "$ART" &
	setsid feh --no-fehbg --bg-scale "$ART"
else
	ART=$( /home/yid/programming/downloader/thumb.py )
	killall -q feh
	setsid feh --no-fehbg --bg-scale "$ART"
fi
