import requests
from datetime import date
# from time import sleep

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


def main():
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    today = date.today()
    cowin_date = "{}-{}-{}".format(today.day, today.month, today.year)

    district_id =265 #Benagluru Urban
    age=18

    # PARAMS = {'district_id ': district_id , 'date': cowin_date}
    URL = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={cowin_date}"
    print(URL)
    try :
        r = requests.get(url=URL)
        print(r.content)
        data = r.json()
        if r.status_code == 400:
            print("Wrong input parameters. Please check. \n")
            exit(0)
        if not data:
            print("Sorry. Not found.\n")
        result = extract_info(data, age)
        if result:
            print('Register now!')
            print_result(result)
            # while(1):
                # playsound('alarm.wav')
            
            # found_vaccine_flag=1

        else:
            print('Can not register yet.')
    except requests.exceptions.ConnectionError:
        print("Connection error.")



if __name__ == '__main__':
    main()