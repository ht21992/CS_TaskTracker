
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

t2 = st.time_input('End Time', datetime.time(
    t.hour + 1 if t.hour < 23 else t.hour, 0))

check_boxes = {}

with st.expander("Advanced Search"):
    c7, c8 = st.columns([0.5, 0.5])
    c9, c10 = st.columns([0.5, 0.5])
    with c8:
        requested_product = st.selectbox("Product Game: ", ('All', 'Games', 'Payments', 'Casino',
                                         'Other', 'Sportsbook', 'Wonder Wheel', 'Skill Games', 'Games', 'Promotion', 'Live Casino'))
    with c7:
        index_column = st.selectbox(
            'Category By:',
            ('Status', 'Product Game', 'Impact Criticality'))
        # requested_status = st.selectbox("Status: ", ('All', 'Closed', 'Ready for Development', 'Cancelled', 'Waiting for BetCo', 'Done', 'Opened', 'Waiting for Reporter', 'Prioritized',
        #                                 'In Progress', 'Backlog', 'Waiting for Review', 'To Do', 'Review', 'On hold', 'Waiting for Approval'))

    for index, cb in enumerate(('Closed', 'Ready for Development', 'Cancelled', 'Waiting for BetCo', 'Done', 'Opened', 'Waiting for Reporter', 'Prioritized',
                                'Rejected', 'In Progress', 'Backlog', 'Waiting for Review', 'To Do', 'Review', 'On hold', 'Waiting for Approval')):
        if index % 2 == 0:
            with c9:
                if index == 0:
                    st.markdown("Choose Status:")
                check_box = st.checkbox(cb)
        else:
            with c10:
                if index == 1:
                    st.markdown("<br>", unsafe_allow_html=True)
                check_box = st.checkbox(cb)
        check_boxes[cb] = check_box


st.write('Date:', d, 'Start Time', t)

st.sidebar.title("HT Task Tracker")

if all(not value for value in check_boxes.values()):
    check_boxes['All'] = True
else:
    check_boxes['All'] = False


EMAIL = st.sidebar.text_input("Enter Your Email Address")
JIRA_TOKEN = st.sidebar.text_input("Enter Your Jira Token", type="password")


def get_issues(email: str, jira_token: str, d: object, t: object, t2: object):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = []
    for startIndex in range(0, 500, 100):
        url = f"http://betconstruct.atlassian.net/rest/api/2/search?jql=project=VHD AND created%20%3E=%20%22{d.year}/{d.month}/{d.day} {t.hour}:{t.minute} %22%20and%20created%20%3C=%20%22{d.year}/{d.month}/{d.day + 1} %22&fields=key,parent,summary,assignee,status,timeestimate,created,updated,customfield_12513,customfield_12512,customfield_12511,reporter,priority,&maxResults=100&startAt={startIndex}"
        response = requests.get(url, headers=headers,
                                auth=(email.strip(), jira_token.strip()))
        try:
            resp = response.json()
            data.extend(resp['issues'])
        except KeyError:
            pass
        except requests.exceptions.JSONDecodeError:
            st.write("Invalid Email or Token")
            break

    return filter_by_timestamp(data, t2)


def filter_by_timestamp(data: list, time):
    filtered_issues = []
    for issue in data:
        try:
            if not check_boxes['All']:
                if not check_boxes[issue['fields']['status']['name']]:
                    continue
        except KeyError:
            continue
        # if requested_status != 'All':
        #     if issue['fields']['status']['name'] != requested_status:
        #         continue

        if requested_product != 'All':
            try :
                if issue['fields']['customfield_12513']['value'] != requested_product:
                    continue
            except TypeError:
                continue

        # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
        issue_date_and_time = issue['fields']['created'].split('T')
        # string format of the time - example -> 10:29:36
        issue_time = issue_date_and_time[1][0:8]
        converted_issue_time = datetime.time(
            int(issue_time[:2]), int(issue_time[3:5]))
        if converted_issue_time >= time:
            pass
        else:
            filtered_issues.append(issue)
    return filtered_issues


def generate_random_hex_color():
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    return hex_number


def make_clickable_both(name): 
    # name, url = val.split('#')
    return f'<a target="_blank" href="https://betconstruct.atlassian.net/browse/{name}">{name}</a>'

if not t >= t2:
    if st.button('Get Issues'):

        data = get_issues(EMAIL, JIRA_TOKEN, d, t, t2)

        if not data:
            st.markdown("Nothing Found")

        else:
            real_data = []
            # colors_dict = {'Ready for Development': '#FFFFF', 'Cancelled': '#F11212', 'Waiting for BetCo': '#072954', 'Done': '#3DE785', 'Opened': '#3DE78D', 'Waiting for Reporter': '#3182ed', 'Prioritized': '#3D9CE7',
            #                'Closed': '#DFCFBE', 'In Progress': '#55B4B0', 'Backlog': '#5B5EA6', 'Waiting for Review': '#EFC050', 'To Do': '#DEE7EC', 'Review': '#B565A7', 'On hold': '#E15D44', 'Waiting for Approval': '#3DE7DE'}

            for issue in data:
                # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                issue_date = issue['fields']['created'].split('T')
                # a list of two strings -> example: ['2023-01-23', '10:56:50.910+0400']
                issue_update = issue['fields']['updated'].split('T')
                # -({issue['fields']['status']['name']})
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
                    skin = ",".join(
                        [sk['value'] for sk in issue['fields']['customfield_12512']])
                except TypeError:
                    skin = 'Unknown'

                # real_data.append(dict(Task=f"{issue['key']}", Start=f'{issue_date[0]} {issue_date[1][:8]}', Finish=f'{issue_update[0]} {issue_update[1][:8]}', Assignee=assignee, Reporter=reporter,
                #                       Status=issue['fields']['status']['name'], Impact_Criticality=impact_criticality, Product_Game=product_game, Skin=skin, Color=colors_dict.get(issue['fields']['status']['name'], generate_random_hex_color())))

                real_data.append(dict(Task=f"{issue['key']}", Start=f'{issue_date[0]} {issue_date[1][:8]}', Finish=f'{issue_update[0]} {issue_update[1][:8]}', Assignee=assignee, Reporter=reporter,
                                      Status=issue['fields']['status']['name'], Impact_Criticality=impact_criticality, Product_Game=product_game, Skin=skin, Color=generate_random_hex_color()))

            df = pd.DataFrame(real_data)
            table_df = df.drop(['Color'], axis=1)

            if df.shape[0] > 36:
                st.markdown('<b style="font-size:12px;color:#DD4124">Too many issues to show in the chart, we suggest to choose shorter time span or apply advanced filters</b>', unsafe_allow_html=True)

            fig = ff.create_gantt(df, show_colorbar=True, colors=df['Color'],
                                  index_col=index_column.replace(' ', '_'))

            # to update legend ==> legend=dict(font=dict(size=8, color="red"))
            fig.update_layout(xaxis=dict(
                title='Timestamp',
                tickformat='%d %B-%Y \n %H:%M:%S',
            ),)
            # # Plot!
            st.plotly_chart(fig, use_container_width=True)

            # Tables
            st.write("Tables")
            st.dataframe(table_df)

            # st.table(df)
            c1, c2, c3 = st.columns([0.5, 0.5, 0.5])
            with c1:
                st.dataframe(df['Status'].value_counts())
            with c2:
                st.dataframe(df['Assignee'].value_counts())
            with c3:
                st.dataframe(df['Product_Game'].value_counts())
            c4, c5, c6 = st.columns([0.5, 0.5, 0.5])
            with c4:
                st.table(df['Skin'].value_counts())
            with c5:
                st.dataframe(df['Reporter'].value_counts())
            with c6:
                st.dataframe(df['Impact_Criticality'].value_counts())

else:
    st.markdown("End Time is more than Start Time")
