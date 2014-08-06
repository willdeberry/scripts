#!/bin/bash

while [ -n "${1}" ]; do
	case "${1}" in
		-w | --work)
			xrandr --output DP3 --off --output DP2 --off --output DP1 --off --output HDMI2 --off --output HDMI3 --mode 1920x1080 --pos 1600x0 --rotate normal --output HDMI1 --off --output LVDS1 --mode 1600x900 --pos 0x0 --rotate normal --output VGA1 --off
			nitrogen --restore
			exit
			;;
		*)
			xrandr --output DP3 --off --output DP2 --off --output DP1 --off --output HDMI3 --off --output VGA1 --mode 1680x1050 --pos 1600x0 --rotate normal --output HDMI1 --off --output LVDS1 --mode 1600x900 --pos 0x0 --rotate normal --output HDMI2 --off
			nitrogen --restore
			exit
			;;
	esac
done
