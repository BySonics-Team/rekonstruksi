import time
import requests
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit
import json
import gc
import os
import sys


Y = 52
M = 129
N = 256
L = Y/N*100
Q = [[0], [0]]
pId = []
Bstart = False
real = []
imag = []
realZ = []
imagZ = []
array = []
i = 0
urlSensor = ''
id_rompi = ""
id_sensor = ""
id_pasien = ""
data = ""
PPG = []
EKG = []
EMG = []
SUHU = []
AcceX = []
AcceY = []
AcceZ = []
ID = []
DataX = []
start = time.time()

for x in range(Y-2):
    Q.append([0])
for x in range(Y):
    for y in range(M-1):
        Q[x].append(0)

Log = 0
Gaussian = np.loadtxt(fname="Gaussian52x129.txt")

for x in range(Y):
    for y in range(M):
        Q[x][y] = Gaussian[Log]
        Log += 1
        
        
def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    led.off()
    print("Auto-reconnect")
    python = sys.executable
    os.execl(python, python, * sys.argv)

    
def kirim_():    
    print("Kirim 1")
    print(PPG)
    print(EKG)
    print(AcceX[:10])
    print(AcceY[:10])
    print(AcceZ[:10])
    print(SUHU)
    print(EMG)
    print(SpO)
    print(HR)
    print(ID)
    data = {
        "id_rompi": ID,
        "id_sensor": "All01",
        "id_pasien": ID,
        "dataAccelerometer_X": AcceX,
        "dataAccelerometer_Y": AcceY,
        "dataAccelerometer_Z": AcceZ,
        "dataSuhu": SUHU,
        "dataEKG": EKG,
        "dataPPG": PPG,
        "dataEMG": EMG,
        "dataSPO2": SpO,
        "dataBPM": HR,
    }
    print("Kirim 2")
    url_POST = (
        'https://bysonics-alpha001-v002.herokuapp.com/dataAllSensor/save')
    print("Kirim 3")
    response = requests.post(url_POST, None, data)
    print("Kirim 4")
    print(f"Request returned {response.status_code} : '{response.reason}'")
    print("Kirim 5")


def CS_(real2, imag2):
    gc.collect()
                
    omp1 = OrthogonalMatchingPursuit()
    omp1.fit(Q, real2)
    coefreal = omp1.coef_

    omp2 = OrthogonalMatchingPursuit()
    omp2.fit(Q, imag2)
    coefimag = omp2.coef_

    realQ = coefreal[0]
    realW = coefreal[M-1]
    realX = coefreal[1:M-1]
    realY = realX[::-1]
    realZ = []
    realZ = np.append(realZ, realQ)
    realZ = np.append(realZ, realX)
    realZ = np.append(realZ, realW)
    realZ = np.append(realZ, realY)

    imagQ = coefimag[0]
    imagW = coefimag[M-1]
    imagX = coefimag[1:M-1]
    imagY = imagX[::-1]*-1
    imagZ = []
    imagZ = np.append(imagZ, imagQ)
    imagZ = np.append(imagZ, imagX)
    imagZ = np.append(imagZ, imagW)
    imagZ = np.append(imagZ, imagY)

    array = []
    for x in range(N):
        com = complex(realZ[x], imagZ[x])
        array = np.append(array, com)

    ftx = []
    ftx = np.fft.ifft(array)

    arr = []
    arr = np.array(ftx.real)
    arr2 = []
    arr2 = arr.tolist()
    myList = []
    myList = [int(x) for x in arr2]
    return myList


def Cek():
    global DataX
    x = requests.get(
        'https://bysonics-alpha001-v002.herokuapp.com/rekonstruksiSensor/Lastest')
    DataX = json.loads(x.text)[0]


try:
    Cek()
    Id = (DataX["_id"])
    pId = (DataX["_id"])
    print("connect to MongoDB")
except:
    id = []
    pId = []
    print("Could not connect to MongoDB")

i = 0
while True:
    try:
        Cek()
        Id = (DataX["_id"])
        if pId != Id:
            start = time.time()
            print(f'Terdapat Data Baru, Id ={Id}')
            Hreal = []
            Himag = []
            try:
                HrealPPG = (DataX["dataPPGReal"])
                HimagPPG = (DataX["dataPPGImag"])
                HrealEKG = (DataX["dataEKGReal"])
                HimagEKG = (DataX["dataEKGImag"])
                HrealACCX = (DataX["dataAccelerometer_XReal"])
                HimagACCX = (DataX["dataAccelerometer_XImag"])
                HrealACCY = (DataX["dataAccelerometer_YReal"])
                HimagACCY = (DataX["dataAccelerometer_YImag"])
                HrealACCZ = (DataX["dataAccelerometer_ZReal"])
                HimagACCZ = (DataX["dataAccelerometer_ZImag"])
                HrealEMG = (DataX["dataEMGReal"])
                HimagEMG = (DataX["dataEMGImag"])
                HrealSUHU = (DataX["dataSuhuReal"])
                HimagSUHU = (DataX["dataSuhuImag"])
                SpO = (DataX["dataSPO2"])
                HR = (DataX["dataBPM"])
                ID = (DataX["id_rompi"])
            except:
                print("Belum Ada Data")
            try:
                PPG = CS_(HrealPPG, HimagPPG)
                EKG = CS_(HrealEKG, HimagEKG)
                AcceX = CS_(HrealACCX, HimagACCX)
                AcceY = CS_(HrealACCY, HimagACCY)
                AcceZ = CS_(HrealACCZ, HimagACCZ)
                SUHU = CS_(HrealSUHU, HimagSUHU)
                EMG = [abs(number) if number >=
                       200 else 0 for number in CS_(HrealEMG, HimagEMG)]
            except:
                print("CS Error")

            #print(SUHU)
            print("CS OK")
            pId = Id
            try:
                kirim_()
                # pass
            except:
                print("Kirim Error")
            end = time.time()
            runTime = end - start
            print(f"Runtime of the program is {runTime} Second")
            print(f'Waiting for new data, Id = {Id}')
        else:
            pass
    except:
        print("Error")
        time.sleep(10)
        try:
            pId = Id
        except:
            pId = []
