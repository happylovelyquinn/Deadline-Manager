from db_controller import *
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os

# we use plotly to draw the gantt chart
# reference https://plotly.com/python/gantt/

def gantt():
    # specify the colours for 4 types of priority
    colors = {'1': 'rgb(250, 200, 189)',
              '2': 'rgb(179, 215, 247)',
              '3': 'rgb(213, 225, 168)',
              '4': 'rgb(210, 210, 211)'}

    # create a directory to store the gantt chart
    if not os.path.exists("images"):
        os.mkdir("images")
    # get the current logged in user
    user = ""
    with open("./user.txt", "r") as f:
        user = f.read()
    if user == '':
        print('please login first')
    else:
        # get the users' uncompleted tasks from the database
        con = sqlite3.connect('./data/database.db')
        df = pd.read_sql_query("SELECT * from TaskTable  WHERE (status = 0 OR status = 2) AND user = '%s'" % user, con)
        # judge whether the user has existing uncompleted tasks
        if df.empty:
            # draw an empty chart if there is no existing uncompleted tasks
            fig = px.timeline(df, x_start="start_date", x_end="end_date", y="task_info", labels={"task_info": None},)
            fig.update_yaxes(autorange="reversed")
            # customise the layout of the  chart
            fig.update_layout(paper_bgcolor='rgb(221, 237, 238)')
            fig.update_layout(plot_bgcolor='rgb(221, 237, 238)')
            # store the chart as a jpeg image
            fig.write_image("images/gantt.jpeg")
        else:
            # draw a gantt chart for existing uncompleted tasks
            # convert the sqlite3 data into a dataframe
            df['task_class'] = df['task_class'].astype("string")
            df2 = pd.DataFrame()
            df2['Task'] = df['task_info']
            df2['Start'] = df['start_date']
            df2['Finish'] = df['end_date']
            df2['Resource'] = df['task_class']

            # draw gantt chart
            # colour index is the number for 4 types of priority
            fig = ff.create_gantt(df2, colors=colors, index_col='Resource', show_colorbar=True,
                                  group_tasks=True, showgrid_x=False, showgrid_y=False, title=None)
            # customise the layout of the chart
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(paper_bgcolor='rgb(221, 237, 238)')
            fig.update_layout(plot_bgcolor='rgb(221, 237, 238)')
            fig.update_layout(
                font_family="Optima",
                font_color="rgb(127, 127, 127)",
            )
            fig.update_layout(
                autosize=False,
                width=421,
                height=321)
            # store the chart as a jpeg image
            fig.write_image("images/gantt.jpeg")

gantt()







