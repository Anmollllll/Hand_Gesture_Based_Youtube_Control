

import cv2
import numpy as np
import pyautogui
import time
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initializing PyCAW and VolumeControl
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volPer = 0

# Gesture Cooldown
gesture_cooldown = False
cooldown_start_time = 0
cooldown_duration = 1.5
last_action_time = 0
current_speed = 1.0

# Playback/Paused
playback_paused = False

# Forward/Backward Keys
seek_time = 5
forward_key = 'right'
backward_key = 'left'

# Speed Keys
SPEED_UP_KEY = '.'
SLOW_DOWN_KEY = ','
PLAY_PAUSE_KEY = 'space'

# Hand stabilization tracking
hand_stable = False
hand_detected_time = 0
hand_stability_threshold = 1.5  # Seconds


def command_youtube(lst, img):
    global gesture_cooldown, cooldown_start_time, cooldown_duration
    global last_action_time, current_speed, playback_paused
    global hand_stable, hand_detected_time

    current_time = time.time()

    if lst and len(lst.landmark) == 21:
        lm = lst.landmark
        if all(0 < i.x < 1 and 0 < i.y < 1 for i in lm):

            # Hand just became stable
            if not hand_stable:
                hand_detected_time = current_time
                hand_stable = True
                cv2.putText(img, "Hold hand steady...", (40, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)
                return current_speed

            # Still within stabilization window
            if current_time - hand_detected_time < hand_stability_threshold:
                cv2.putText(img, "Hold hand steady...", (40, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)
                return current_speed

            # Visual feedback when ready
            cv2.putText(img, "Hand ready for gesture", (40, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 3)
            
            #Setting up finger variables
            index_finger_up = is_finger_up(lm[8], lm[6], lm[5])
            middle_finger_up = is_finger_up(lm[12], lm[10], lm[9])
            ring_finger_up = is_finger_up(lm[16], lm[14], lm[13])
            pinky_finger_up = is_finger_up(lm[20], lm[18], lm[17])
            thumb_up = ((lm[4].x - lm[5].x) ** 2 + (lm[4].y - lm[5].y) ** 2) ** 0.5 > 0.1

            #Identifying hand
            hand = identify_hand(lm)
            
            # If in general cooldown,wait for fingers to go down before resetting
            if gesture_cooldown:
                if current_time - cooldown_start_time >= cooldown_duration:
                    gesture_cooldown = False
                else:
                    return current_speed

            if hand == 'Left':
                if index_finger_up and thumb_up and not (middle_finger_up or ring_finger_up or pinky_finger_up):
                    frameWidth, frameHeight = img.shape[1], img.shape[0]
                    x1 = int(lm[4].x * frameWidth)
                    y1 = int(lm[4].y * frameHeight)
                    x2 = int(lm[8].x * frameWidth)
                    y2 = int(lm[8].y * frameHeight)

                    cv2.circle(img, (x1, y1), 15, (255, 255, 0), cv2.FILLED)
                    cv2.circle(img, (x2, y2), 15, (255, 255, 0), cv2.FILLED)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 3)
                    length = int(math.hypot(x2 - x1, y2 - y1))
                    vol = np.interp(length, [50, 160], [minVol, maxVol])
                    volBar = np.interp(length, [50, 160], [400, 150])
                    volPer = np.interp(length, [50, 160], [0, 100])
                    volume.SetMasterVolumeLevel(vol, None)
                    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
                    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                    if pinky_finger_up:
                        gesture_cooldown = True
                        cooldown_start_time = current_time
                    

                elif thumb_up and not (index_finger_up or middle_finger_up or ring_finger_up or pinky_finger_up):
                    pyautogui.press(forward_key)
                    cv2.putText(img, f'Seeking forward {seek_time} seconds', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,(255, 0, 0), 3)
                    gesture_cooldown = True
                    cooldown_start_time = current_time
                    

            if hand == 'Right':
                if index_finger_up and not (middle_finger_up or ring_finger_up or pinky_finger_up or thumb_up):
                    pyautogui.hotkey('shift', SPEED_UP_KEY)
                    current_speed += 0.25
                    last_action_time = current_time
                    cv2.putText(img, f'Speeding up to: {current_speed:.2f}x', (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                    gesture_cooldown = True
                    cooldown_start_time = current_time
                    

                elif pinky_finger_up and not (index_finger_up or middle_finger_up or ring_finger_up or thumb_up):
                    pyautogui.hotkey('shift', SLOW_DOWN_KEY)
                    current_speed -= 0.25
                    last_action_time = current_time
                    cv2.putText(img, f'Slowing down to: {current_speed:.2f}x', (40, 100), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0), 3)
                    gesture_cooldown = True
                    cooldown_start_time = current_time
                    

                elif index_finger_up and middle_finger_up and ring_finger_up and pinky_finger_up and not thumb_up:
                    if current_time - cooldown_start_time >= cooldown_duration:
                        pyautogui.press(PLAY_PAUSE_KEY)
                        playback_paused = not playback_paused
                        cv2.putText(img, f"Playback {'paused' if playback_paused else 'playing'}", (40, 100),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                        gesture_cooldown = True
                        cooldown_start_time = current_time
                    

                elif thumb_up and not (index_finger_up or middle_finger_up or ring_finger_up or pinky_finger_up):
                    pyautogui.press(backward_key)
                    cv2.putText(img, f'Seeking Backward {seek_time} seconds', (40, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 0), 3)
                    gesture_cooldown = True
                    cooldown_start_time = current_time
                    

        else:
            hand_stable = False  # reset if landmarks are invalid
            return current_speed

    else:
        hand_stable = False  # reset if no hand
        return current_speed


def is_finger_up(tip, pip, mcp):
    return tip.y < pip.y < mcp.y


def identify_hand(lm):
    if lm[5].x > lm[17].x:
        return 'Left'
    else:
        return 'Right'
