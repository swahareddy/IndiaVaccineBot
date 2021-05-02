# import look_per_pin
from datetime import date
from time import sleep
import requests
import telegram_send
import io
from contextlib import redirect_stdout


def main():
    city_details={'pune':{'start':411000, 'end':411053}}
    city_details={'bengaluru':{'start':560001, 'end':560105}}
    
    city='bengaluru'
    age=25
    
    pin_start=city_details[city]['start']
    pin_end=city_details[city]['end']
    
    # idx = 0
    retry_in=120
    while (1):
    # time_elapsed = idx * retry_in
        i=pin_start
        hospitals_with_vaccine=[]

        while i<=pin_end:
            print(i)
            result_per_pin=look_per_pin(i, age)
            if result_per_pin['flag']:
                hospitals_with_vaccine.append(result_per_pin['hospitals_with_vaccine'])
            i+=1

        if len(hospitals_with_vaccine)>0:
            telegram_send.send(messages=hospitals_with_vaccine)
        sleep(retry_in)
    # idx += 1


def extract_info(data, age):
    result = []
    centers = data['centers']
    for center in centers:
        center_name = center['name']
        centre_pincode = center['pincode']
        district_name = center['district_name']
        block_name = center['block_name']
        centre_fee = center['fee_type']
        sessions = center['sessions']
        temp_result = []
        for session in sessions:
            available_capacity = int(session['available_capacity'])
            if available_capacity == 0:
                continue

            session_age = int(session['min_age_limit'])
            if session_age > age:
                continue
            session_date = session['date']
            session_vaccine = session['vaccine']
            if session_vaccine == '':
                session_vaccine = 'unknown'
            row = (available_capacity, session_age,
                   session_date, session_vaccine)
            temp_result.append(row)
        if temp_result != []:
            address = (center_name, centre_pincode,
                       district_name, block_name, centre_fee)
            row = (address, temp_result)
            result.append(row)

    return result

def print_result(result):
    print("\n\n")
    if result == []:
        print("Sorry, no centers for your parameters.\n")
        return
    for row in result:
        print("CENTER DETAILS")
        address = row[0]
        sessions = row[1]
        print("Center Name - {}\nCenter Pin Code - {}\nDistrict - {}\nBlock - {}\nCentre Fee - {}\n".format(*address))
        print("Printing Sessions for this center:")
        for session in sessions:
            print("For", session[2], end='\t')
            print("{} doses available with minimum age {} and vaccine {}".format(
                session[0], session[1], session[3]))
        print("\n")

def look_per_pin(pin, age):
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
    today = date.today()
    cowin_date = "{}-{}-{}".format(today.day, today.month, today.year)
    PARAMS = {'pincode': pin, 'date': cowin_date}

    captured_output=''
    found_vaccine_flag = 0
    
    try:
        r = requests.get(url=URL, params=PARAMS)
        data = r.json()
        if r.status_code == 400:
            print("Wrong input parameters. Please check. \n")
            exit(0)
        if not data:
            print("Sorry. Not found.\n")
        result = extract_info(data, age)
        if result:
            print('Register now!')
            f = io.StringIO()
            with redirect_stdout(f):
                print_result(result)
            captured_output = f.getvalue()
            
            # while(1):
                # playsound('alarm.wav')
            
            found_vaccine_flag=1

        else:
                print('Can not register yet.')
    except requests.exceptions.ConnectionError:
        print("Connection error.")

    return {'flag':found_vaccine_flag, 'hospitals_with_vaccine':captured_output}

if __name__ == '__main__':
    main()