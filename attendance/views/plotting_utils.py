import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List

from attendance.models import GosStudent
from attendance.models.date_ranges import get_filter_attendance_by_date_range_query
from attendance.views.utils import get_recommended_hour_series


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


def render_cumulative_hours_plot(students, recommended_hours: List[Dict]):
    cum_hours = []
    names = []
    num_meetings = []
    for student in students:
        names.append(student.full_name())
        cum_hours.append(student.num_hours())
        num_meetings.append(student.num_meetings())
    df = pd.DataFrame(
        {"name": names, "hours": cum_hours, "meetings": num_meetings}
    ).sort_values(by="name")

    fig = px.bar(df, x="name", y="hours")

    for line_settings in recommended_hours:
        fig.add_hline(**line_settings)

    return render_html_figure(fig)


def render_hours_scatter(student: GosStudent):
    sum_hours = 0
    timestamp_data = []
    sum_hours_data = []
    hours_data = []

    for att in student.gosattendance_set.filter(
        **get_filter_attendance_by_date_range_query()
    ):

        hours = att.get_duration().total_seconds() / 3600
        sum_hours += hours
        hours_data.append(hours)
        timestamp_data.append(
            att.time_in.replace(hour=0, minute=0, second=0, microsecond=0)
        )
        sum_hours_data.append(sum_hours)

    hour_series = get_recommended_hour_series()
    hours_dates, *hours_plots = hour_series

    plots = []
    plots.append(
        go.Scatter(
            x=timestamp_data,
            y=sum_hours_data,
            mode="markers",
            name="Cumulative Hours",
        )
    )
    for title, hp in hours_plots:
        plots.append(go.Scatter(x=hours_dates, y=hp, name=title, mode="lines+markers"))
    plots.append(go.Bar(x=timestamp_data, y=hours_data, name="Meeting Hours"))
    fig = go.Figure(plots)

    return render_html_figure(fig)
