import os
import datetime


os.path.isfile(file_name)
def generate_manualscan_csv(form_data):
    todayDate = datetime.date.today()
    if todayDate.day == 1:
        t = datetime.datetime.now()
        formatted_time = t.strftime('%B-%Y')
        file_name = '{}.csv'.format(formatted_time)
        with open(file_name, 'w') as csvfile:
            filewriter = csv.writer(
                csvfile, delimiter=',')
            filewriter.writerow([
                'app_name', 'app_env',
                'min_os_version', 'app_action',
                'login_required', 'user_roles',
                'vpn_required', 'vpn_details',
                'contact', 'additional_comments'
            ])
            filewriter.writerow([
                form_data['app_name'],
                form_data['app_env'],
                form_data['min_os_version'],
                form_data['app_action'],
                form_data['login_required'],
                form_data['user_roles'],
                form_data['vpn_required'],
                form_data['vpn_details'],
                form_data['contact'],
                form_data['additional_comments'],
            ])

    t = datetime.datetime.now()
    formatted_time = t.strftime('%B-%Y')
    file_name = '{}.csv'.format(formatted_time)
    with open(file_name, 'a') as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=',')
        filewriter.writerow([
            form_data['app_name'],
            form_data['app_env'],
            form_data['min_os_version'],
            form_data['app_action'],
            form_data['login_required'],
            form_data['user_roles'],
            form_data['vpn_required'],
            form_data['vpn_details'],
            form_data['contact'],
            form_data['additional_comments'],
        ])