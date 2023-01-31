#Auhor: Jakob Metzler, Otto Cibulka

#Importieren der benötigten µPython-Bibliotheken:
import pyb, sensor, image, time
from pyb import UART

#Initalisierung des Sensors:
sensor.reset() #Rücksetzen der vorhandenen Einstellungen
sensor.set_pixformat(sensor.RGB565) #Farbformat für Pixel wählen, hier: RGB256 --> 256-bit Rot Grün Blau Zahl
sensor.set_framesize(sensor.QVGA) #Captureframe Auflösung festlegen, hier: QVGA 320x240 (QVGA = Quarter VGA ==> ein viertel der VGA Auflösung)
sensor.set_vflip(False) #Mögliche Bildkorrektur im Bezug auf vertikale Ausrichtung
sensor.set_hmirror(False) #Mögliche Bildkorrektur im Bezug auf horizontale Spiegelung
sensor.skip_frames(time = 2000) #Für Bildstabiliserung übersprungene Frames

#Definieren von Objekten der Onboard-RGB-Led
red_led = pyb.LED(1)
green_led = pyb.LED(2)
blue_led = pyb.LED(3)

#Ermitteln der Bildkoordinate des relativen Koordinatenursprungs
def getOrigin(blobs):
    blobs.sort(key=lambda x: x.cy(), reverse=True)

    if (blobs[0].cx() < blobs[1].cx()):
        return blobs[0]
    else:
        return blobs[1]

def getBottomRight(blobs):
    blobs.sort(key=lambda x: x.cy(), reverse=True)

    print(blobs)

    if (blobs[0].cx() > blobs[1].cx()):
        return blobs[0]
    else:
        return blobs[1]

def getTopLeft(blobs):
    blobs.sort(key=lambda x: x.cy())

    print(blobs)

    if (blobs[0].cx() < blobs[1].cx()):
        return blobs[0]
    else:
        return blobs[1]

def getTopRight(blobs):
    blobs.sort(key=lambda x: x.cy())

    print(blobs)

    if (blobs[0].cx() > blobs[1].cx()):
        return blobs[0]
    else:
        return blobs[1]

def getSortedBlobs(blobs):
    return [getOrigin(blobs), getBottomRight(blobs), getTopLeft(blobs), getTopRight(blobs)]

#RGB Led Rot setzen
def setLedRed():
    red_led.on()
    green_led.off()
    blue_led.off()

#RGB Led Grün setzen
def setLedGreen():
    red_led.off()
    green_led.on()
    blue_led.off()

#RGB Led Blau setzen
def setLedBlue():
    red_led.off()
    green_led.off()
    blue_led.on()

#Arbeitsschleife
while(True):
    time.sleep(0.01)
    #Definieren der Farbbereiche zur Erkennung der Markierungen
    thresholdCorner = (0, 100, 21, 66, 8, 127)
    thresholdTrain1 = (0, 63, -25, 48, -47, -16)
    thresholdTrain2 = (45, 75, -23, 5, 40, 80)
    xPixelToMMScale = 4.59;
    yPixelToMMScale = 4.74;
    xOffset = 2388;
    yOffset = 70;
    try: # Abfangen möglicher Frame-Buffer Probleme in der Runtime
        img = sensor.snapshot() #Zwischenspeichern des aktuellen Bilds

        blobsCorner = img.find_blobs([thresholdCorner], area_threshold=25, merge=True) #Suchen nach Eck-Markierungen

        if (len(blobsCorner) == 4): #Überprüfen ob ein Bereich definiert werden kann
            setLedGreen() #LED grün setzen um Erfolg bei der Bereichdefinierung anzuzeigen
            for b in blobsCorner:
                img.draw_circle(b.x(), b.y(), 10, color = (255, 0, 0))

            blobOrigin = getOrigin(blobsCorner) #Ermitteln des relativen Koordinaten Urpsrungs (links unten)
            blobsTrain1 = img.find_blobs([thresholdTrain1], area_threshold=25, merge=True) #Suchen nach Zug1 im definierten Bildbereich
            blobsTrain2 = img.find_blobs([thresholdTrain2], area_threshold=20, merge=True) #Suchen nach ZUg2 im definierten Bildbereich

            if (len(blobsTrain1) > 0): #Falls Zug1 gefunden wurde
                setLedBlue() #Indikator-Led blau setzen um gefundenen Zug anzuzeigen
                img.draw_circle(blobsTrain1[0].x(), blobsTrain1[0].y(), 10, color = (0,255,0))
                outputX = xPixelToMMScale*(blobsTrain1[0].cx() - blobOrigin.cx()) + xOffset # Berechnen der relativen X-Koordinate in mm
                outputY = yPixelToMMScale*(blobOrigin.cy() - blobsTrain1[0].cy()) + yOffset # Berechnen der relativen Y-Koordiante in mm
                if (outputX > 0 and outputY > 0): #Ausgabe der Zug-Koordinaten via USB
                    print("*0:" + str(int(outputX)) + ":" + str(int(outputY)) + ";")
            if (len(blobsTrain2) > 0): #Falls Zug2 gefunden wurde
                setLedBlue() #Indikator-Led blau setzen um gefunden Zug anzuzeigen
                img.draw_circle(blobsTrain2[0].x(), blobsTrain2[0].y(), 10, color = (0,0,255))
                outputX = xPixelToMMScale*(blobsTrain2[0].cx() - blobOrigin.cx()) + xOffset # Berechnen der relativen X-Koordinate
                outputY = yPixelToMMScale*(blobOrigin.cy() - blobsTrain2[0].cy()) + yOffset # Berechnen der relativen Y-Koordinate
                if (outputX > 0 and outputY > 0): #Ausgabe der Zug-Koordinaten via UART
                    print("*1:" + str(int(outputX)) + ":" + str(int(outputY)) + ";")
        else:
            setLedRed() #Indikator-Led rot setzen falls kein definierbarer Bereich gefunden wurde
        time.sleep(0.1)
    except:
        time.sleep(0.1) #Eine Sekunde warten um im falle eines Runtime Frame-Errors die Capture wieder neu laden zu lassen



