import asyncio
import cv2
import numpy as np
import websockets
import base64
import json
import os
# CORONA_TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/corona_template.png'
# print(CORONA_TEMPLATE_PATH)

# CORONA_SCALE_RATIO = 0.5

# corona_template_image = cv2.imread(CORONA_TEMPLATE_PATH, 0)

# corona_template_image = cv2.resize(corona_template_image, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)


# def catch_corona(wave_image, threshold=0.95):
#     catchCorona = []
#     for x in range(1, 17):
#         hinh= cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/corona/corona-%d.png' %x)
#         print(hinh)
#         hinh = cv2.resize(hinh, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
#         wave_image_gray = cv2.cvtColor(wave_image, cv2.COLOR_BGRA2GRAY)
#         template_gray = cv2.cvtColor(hinh, cv2.COLOR_BGRA2GRAY)

#         res = cv2.matchTemplate(wave_image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

#         if max_val <= threshold:
#             width, height = corona_template_image.shape[::-1]
#             top_left = max_loc
#             bottom_right = (top_left[0] + width, top_left[1] + height)
#             catchCorona.append([top_left, bottom_right])
#     return catchCorona

CORONA_TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/characters/character-1.png'
CORONA_SCALE_RATIO = 0.5
corona_template_image = cv2.imread(CORONA_TEMPLATE_PATH, 0)
corona_template_image = cv2.resize(corona_template_image, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
image_Docter_Paitent = []
image_Docter_Paitent.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/bacsi/trudiem-1.png'))
image_Docter_Paitent.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/bacsi/trudiem-2.png'))
image_Corona = []
image_Corona.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/corona/corona-4.png'))
image_Corona.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/corona/corona-3.png'))
image_Corona.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/corona/corona-2.png'))
image_Corona.append(cv2.imread(r'D:/KMS-Gotcha/gotcha-corona-player/corona/corona-1.png'))
def catch_Corona(wave_image, threshold=0.75):
    wave_image_gray = cv2.cvtColor(wave_image, cv2.COLOR_BGRA2GRAY)
    width, height = corona_template_image.shape[::-1]
    array_Coronas = []
    array_Doctors_Paitents = []
    # catch doctor & paitent
    for image in image_Docter_Paitent:
        image = cv2.resize(image, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
        template_gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(wave_image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= 0.6)
        for pt in zip(*loc[::-1]):
            array_Doctors_Paitents.append([pt,(pt[0] + width, pt[1] + height)])
    # catch corona
    for image in image_Corona:
        image = cv2.resize(image, None, fx=CORONA_SCALE_RATIO, fy=CORONA_SCALE_RATIO)
        template_gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(wave_image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            array_Coronas.append([pt,(pt[0] + width, pt[1] + height)])
    # delete position doctor
    result=[]
    for array_corona in array_Coronas:
        count=0
        for array_Doctor_Paitent in array_Doctors_Paitents:
            if(((array_corona[0][0] + array_corona[1][0]) / 2 > array_Doctor_Paitent[0][0] and (array_corona[0][0] + array_corona[1][0]) / 2 < array_Doctor_Paitent[0][0])
            or ((array_corona[0][1] + array_corona[1][1]) / 2 > array_Doctor_Paitent[0][1] and (array_corona[0][1] + array_corona[1][1]) / 2 < array_Doctor_Paitent[1][1])):
                break
            else :
                count=count+1
        if(len(array_Doctors_Paitents)==count):
            result.append(array_corona)
    return result
def base64_to_image(base64_data):
    encoded_data = base64_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    return img
async def play_game(websocket, path):
    print('Corona Killer is ready to play!')
    catchings = []
    last_round_id = ''
    wave_count = 0
    while True:
        ### receive a socket message (wave)
        try:
            data = await websocket.recv()
        except Exception as e:
            print('Error: ' + e)
            break

        json_data = json.loads(data)

        ### check if starting a new round
        if json_data["roundId"] != last_round_id:
            print(f'> Catching corona for round {json_data["roundId"]}...')
            last_round_id = json_data["roundId"]

        ### catch corona in a wave image
        wave_image = base64_to_image(json_data['base64Image'])
        results = catch_Corona(wave_image)
        ### save result image file for debugging purpose
        for result in results:
            cv2.rectangle(wave_image, result[0], result[1], (0, 0, 255), 2)
        
        waves_dir = f'waves/{last_round_id}/'
        if not os.path.exists(waves_dir):
            os.makedirs(waves_dir)
        cv2.imwrite(os.path.join(waves_dir, f'{json_data["waveId"]}.jpg'), wave_image)

        print(f'>>> Wave #{wave_count:03d}: {json_data["waveId"]}')
        wave_count = wave_count + 1
        ### store catching positions in the list
        catchings.append({
            "positions": [
                
                {"x": (result[0][0] + result[1][0]) / 2, "y": (result[0][1] + result[1][1]) / 2} for result in results
            ],
            "waveId": json_data["waveId"]
        })
        ### send result to websocket if it is the last wave
        if json_data["isLastWave"]:
            round_id = json_data["roundId"]
            print(f'> Submitting result for round {round_id}...')

            json_result = {
                "roundId": round_id,
                "catchings": catchings,
            }

            await websocket.send(json.dumps(json_result))
            print('> Submitted.')

            catchings = []
            wave_count = 0
start_server = websockets.serve(play_game, "localhost", 8765, max_size=100000000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


