import cv2 
import mediapipe as mp
import gesture_fnc



cap = cv2.VideoCapture(0)
drawing = mp.solutions.drawing_utils
hands = mp.solutions.hands
hand_obj = hands.Hands(max_num_hands=1)


while True:
    check, fm = cap.read()
    fm = cv2.flip(fm, 1)

    rbg = hand_obj.process(cv2.cvtColor(fm, cv2.COLOR_BGR2RGB))

    if rbg.multi_hand_landmarks:

        hand_keyPoints = rbg.multi_hand_landmarks[0]
        gesture_fnc.command_youtube(hand_keyPoints,fm)
        drawing.draw_landmarks(fm, hand_keyPoints, hands.HAND_CONNECTIONS)

    cv2.imshow("window", fm)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.release()
        break