import cv2
import numpy as np
import pyautogui
from cvzone.HandTrackingModule import HandDetector

pyautogui.FAILSAFE = False

largura_cam, altura_cam = 640, 480
webcam = cv2.VideoCapture(0)
webcam.set(3, largura_cam)
webcam.set(4, altura_cam)

largura_tela, altura_tela = pyautogui.size()

margem = 40

suavizacao = 5
plocX, plocY = 0, 0
clocX, clocY = 0, 0

detector = HandDetector(detectionCon=0.8, maxHands=1)

print("--- MOUSE VIRTUAL ATIVO ---")

while webcam.isOpened():
    sucesso, frame = webcam.read()
    if not sucesso:
        print("Erro na captura da webcam.")
        break

    frame = cv2.flip(frame, 1)

    hands, frame = detector.findHands(frame, draw=True)

    cv2.rectangle(frame, (margem, margem), 
                  (largura_cam - margem, altura_cam - margem), 
                  (255, 0, 255), 2)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]  
        dedos = detector.fingersUp(hand) 

        x1, y1 = lmList[8][0], lmList[8][1]
        x2, y2 = lmList[12][0], lmList[12][1]
        x0, y0 = lmList[4][0], lmList[4][1]

        if dedos[1] == 1 and dedos[2] == 0:
            x3 = np.interp(x1, (margem, largura_cam - margem), (0, largura_tela))
            y3 = np.interp(y1, (margem, altura_cam - margem), (0, altura_tela))

            x3 = np.clip(x3, 0, largura_tela)
            y3 = np.clip(y3, 0, altura_tela)

            clocX = plocX + (x3 - plocX) / suavizacao
            clocY = plocY + (y3 - plocY) / suavizacao

            pyautogui.moveTo(clocX, clocY)
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        if dedos[1] == 1 and dedos[2] == 1:
            distancia, _, frame = detector.findDistance((x1, y1), (x2, y2), frame)
            if distancia < 35:
                cv2.circle(frame, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                pyautogui.sleep(0.15)

        distancia_dir, _, frame = detector.findDistance((x0, y0), (x1, y1), frame)
        if distancia_dir < 40 and dedos[2] == 0:
            cv2.circle(frame, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            pyautogui.rightClick()
            pyautogui.sleep(0.3)

    cv2.imshow("Mouse Virtual - Controle por Gestos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()