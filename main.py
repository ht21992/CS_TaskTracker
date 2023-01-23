

import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.figure_factory as ff
# Change page names on Side bar
st.set_page_config(
    page_title="Task Tracker",
)


d = st.date_input(
    "Select Date",
    datetime.datetime.now())
t = st.time_input('Start Time', datetime.time(8, 45))

t2 = st.time_input('End Time', datetime.time(t.hour + 1 if t.hour < 23 else t.hour, 0))

st.write('Date:', d, 'Start Time', t)

st.sidebar.title("HT Task Tracker")
EMAIL= st.sidebar.text_input("Enter Your Email Address")
JIRA_TOKEN = st.sidebar.text_input("Enter Your Jira Token", type="password")


def get_issues(email:str, jira_token:str, d:object,t:object,t2:object):

    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
    data = []
    for startIndex in range(0, 5, 1):
        url = f"http://betconstruct.atlassian.net/rest/api/2/search?jql=created%20%3E=%20%22{d.year}/{d.month}/{d.day} {t.hour}:{t.minute} %22%20and%20created%20%3C=%20%22{d.year}/{d.month}/{d.day + 1} %22&project=VHD&fields=key,parent,summary,assignee,status,timeestimate,created,updated,&maxResults=100&startAt={startIndex}"

  
        response = requests.get(url, headers=headers,
                                auth=(email, jira_token))

        
        try:
            resp = response.json()
            data.extend(resp['issues'])
        except KeyError:
            pass
        except requests.exceptions.JSONDecodeError:
            st.write("Invalid Email or Token")
            break

    return filter_by_timestamp(data,t2)



def filter_by_timestamp(data: list, time):
    filtered_issues = []
    for issue in data:
        issue_date_and_time = issue['fields']['created'].split('T')  # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
        issue_time = issue_date_and_time[1][0:8] # string format of the time - example -> 10:29:36 
        converted_issue_time = datetime.time(int(issue_time[:2]),int(issue_time[3:5]))
        if converted_issue_time >= time:
            pass
        else:
            filtered_issues.append(issue)
    
    return filtered_issues





if not t >= t2:
    if st.button('Get Issues'):
        
        data = get_issues(EMAIL,JIRA_TOKEN,d,t,t2)
        

        if not data:
            st.markdown("Nothing Found")

        else:
            real_data = []
            colors_dict = {'Cancelled':'#F11212','Waiting for BetCo':'#Eb008a','Done':'#3DE785','Opened':'#3DE78D','Waiting for Reporter':'#FFFFFF','Prioritized':'#3D9CE7','Closed':'#DFCFBE', 'In Progress':'#55B4B0','Backlog':'#5B5EA6', 'Waiting for Review':'#EFC050','To Do':'#DEE7EC','Review':'#B565A7','On hold':'#E15D44','Waiting for Approval':'#3DE7DE'}
            for issue in data:
                issue_date = issue['fields']['created'].split('T')  # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                issue_update = issue['fields']['updated'].split('T')  # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                real_data.append(dict(Task=f"{issue['key']}", Start=f'{issue_date[0]} {issue_date[1][:8]}',Finish=f'{issue_update[0]} {issue_update[1][:8]}',Assignee =issue['fields']['assignee']['displayName'] ,Status=issue['fields']['status']['name'],Color=colors_dict.get(issue['fields']['status']['name'])))

            df = pd.DataFrame(real_data)
            c1,c2 = st.columns([0.5,0.5])
            with c1:
                st.table(df['Status'].value_counts())
            with c2:
                st.table(df['Assignee'].value_counts())
            
            
            fig = ff.create_gantt(df,show_colorbar=True,index_col='Status',colors=list(map(lambda x: x, df['Color'])))
            fig.update_layout(xaxis=dict(
                                title='Timestamp', 
                                tickformat = '%d %B-%Y \n %H:%M:%S',
                            ))

            st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown("End Time is more than Start Time")

