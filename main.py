
# Import libraries
import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.figure_factory as ff
import random
# Change page names on Side bar
st.set_page_config(
    page_title="Task Logger",
)


# Css

style = """
<style>
@import url("https://fonts.googleapis.com/css?family=Sofia");


button[title="View fullscreen"]{
    visibility: hidden;}


.css-1ec096l {
    font-size: 12px;
    font-family: "Source Sans Pro", sans-serif;
    padding: 0.25rem 0.375rem;
    line-height: 1.5;
    overflow: overlay;
    text-align: center;
}
</style>
"""

#  css part
st.write(style, unsafe_allow_html=True)




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
    for startIndex in range(0, 500, 100):
        url = f"http://betconstruct.atlassian.net/rest/api/2/search?jql=project=VHD AND created%20%3E=%20%22{d.year}/{d.month}/{d.day} {t.hour}:{t.minute} %22%20and%20created%20%3C=%20%22{d.year}/{d.month}/{d.day + 1} %22&fields=key,parent,summary,assignee,status,timeestimate,created,updated,customfield_12513,customfield_12512,customfield_12511,reporter,priority,&maxResults=100&startAt={startIndex}"
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


def generate_random_hex_color():
    random_number = random.randint(0,16777215)
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    return hex_number


if not t >= t2:
    if st.button('Get Issues'):
        
        data = get_issues(EMAIL,JIRA_TOKEN,d,t,t2)
        

        if not data:
            st.markdown("Nothing Found")

        else:
            real_data = []
            colors_dict = {'Ready for Development':'#FFFFF','Cancelled':'#F11212','Waiting for BetCo':'#FF00FF','Done':'#3DE785','Opened':'#3DE78D','Waiting for Reporter':'#FFFFFF','Prioritized':'#3D9CE7','Closed':'#DFCFBE', 'In Progress':'#55B4B0','Backlog':'#5B5EA6', 'Waiting for Review':'#EFC050','To Do':'#DEE7EC','Review':'#B565A7','On hold':'#E15D44','Waiting for Approval':'#3DE7DE'}
           
            for issue in data:
                issue_date = issue['fields']['created'].split('T')  # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                issue_update = issue['fields']['updated'].split('T')  # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                #-({issue['fields']['status']['name']})
                try:
                    assignee = issue['fields']['assignee']['displayName']
                except TypeError:
                    assignee = 'Unknown'
                try:
                    reporter = issue['fields']['reporter']['displayName']
                except TypeError:
                    reporter = 'Unknown'
                try:
                    product_game = issue['fields']['customfield_12513']['value']
                except TypeError:
                    product_game = 'Unknown'
                
                try:
                    impact_criticality = issue['fields']['customfield_12511']['value']
                except TypeError:
                    impact_criticality = 'Unknown'
                try:
                    skin = ",".join([sk['value'] for sk in issue['fields']['customfield_12512']])
                except TypeError:
                    skin = 'Unknown'
                
                real_data.append(dict(Task=f"{issue['key']}", Start=f'{issue_date[0]} {issue_date[1][:8]}',Finish=f'{issue_update[0]} {issue_update[1][:8]}',Assignee= assignee,Reporter=reporter,Status=issue['fields']['status']['name'],Impact_Criticality=impact_criticality,Product_Game=product_game,Skin=skin,Color=colors_dict.get(issue['fields']['status']['name'],generate_random_hex_color())))
   
            df = pd.DataFrame(real_data)
            table_df = df.drop(['Color'], axis=1)

            print('done')
            
            
            fig = ff.create_gantt(df,show_colorbar=True,index_col='Status',colors=list(map(lambda x: x, df['Color'])))
            fig.update_layout(xaxis=dict(
                                title='Timestamp', 
                                tickformat = '%d %B-%Y \n %H:%M:%S',
                            ))

            # # Plot!
            st.plotly_chart(fig, use_container_width=True)
            st.write("Tables")
            st.table(table_df)
            c1,c2,c3 = st.columns([0.5,0.5,0.5])
            with c1:
                st.table(df['Status'].value_counts())
            with c2:
                st.table(df['Assignee'].value_counts())
            with c3:
                st.table(df['Product_Game'].value_counts())
            c4,c5,c6 = st.columns([0.7,0.5,0.5])
            with c4:
                st.table(df['Skin'].value_counts())
            with c5:
                st.table(df['Reporter'].value_counts())
            with c6:
                st.table(df['Impact_Criticality'].value_counts())
            
else:
    st.markdown("End Time is more than Start Time")

