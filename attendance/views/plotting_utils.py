import plotly.express as px
import plotly.graph_objects as go
import pandas as pd



def render_html_figure(figure):
    return figure.to_html(full_html=False, include_plotlyjs="cdn")


def render_count_pie_chart(df, count_groupby_key, field_name, title):
    grouped_df = df.groupby(count_groupby_key).count()[field_name]

    values = grouped_df.values
    names = grouped_df.index.values

    figure = go.Figure(data=[go.Pie(labels=names, values=values)])
    figure.update_layout(title={"text": title})

    return render_html_figure(figure)


def render_box_and_whisker_plot(df, groupby_key, field_name, title):
    return render_html_figure(
        px.box(df, x=groupby_key, y=field_name, points="all", title=title)
    )


def render_cumulative_hours_plot(students):
    cum_hours = []
    names = []
    num_meetings = []
    for student in students:
        names.append(student.full_name())
        cum_hours.append(student.num_hours())
        num_meetings.append(student.num_meetings())
    df = pd.DataFrame(
        {"name": names, "hours": cum_hours, "meetings": num_meetings}
    ).sort_values(by="hours")

    return render_html_figure(px.bar(df, x="name", y="hours", color="meetings"))
