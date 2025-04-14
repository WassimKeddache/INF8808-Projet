import plotly.express as px


def get_empty_figure():
    fig = px.line()
    fig.update_layout(dragmode=False, xaxis_visible=False, yaxis_visible=False)
    fig.add_annotation(
        text="No data to display. Select an element in the barchart for more information",
        showarrow=False,
        xref="paper",
        yref="paper",
    )
    return fig


def add_rectangle_shape(fig):
    """
    Adds a rectangle to the figure displayed
    behind the informational text. The color
    is the 'pale_color' in the THEME dictionary.

    The rectangle's width takes up the entire
    paper of the figure. The height goes from
    0.25% to 0.75% the height of the figure.
    """
    # TODO : Draw the rectangle
    fig.add_shape(
        type="rect",
        fillcolor=THEME["pale_color"],
        line_color=THEME["pale_color"],
        opacity=1,
        xref="x domain",
        yref="y domain",
        x0=0,
        x1=1,
        y0=0.0025,
        y1=0.0075,
    )

    return fig


def get_figure(film_data, actor):
    """
    Generates the line chart using the given data.

    The ticks must show the zero-padded day and
    abbreviated month. The y-axis title should be 'Trees'
    and the title should indicated the displayed
    neighborhood and year.

    In the case that there is only one data point,
    the trace should be displayed as a single
    point instead of a line.

    Args:
        line_data: The data to display in the
        line chart
        arrond: The selected neighborhood
        year: The selected year
    Returns:
        The figure to be displayed
    """
    # TODO : Construct the required figure. Don't forget to include the hover template
    non_zero_count = line_data["Counts"].ne(0).sum()

    fig = (
        px.line(line_data, x="Date_Plantation", y="Counts")
        if non_zero_count != 1
        else px.scatter(line_data, x="Date_Plantation", y="Counts")
    )

    fig.update_traces(hovertemplate=hover_template.get_linechart_hover_template())

    fig.update_layout(
        title=f"Trees planted in {arrond} in {year}",
        xaxis_title=" ",
        yaxis_title="Trees",
        xaxis=dict(tickformat="%d %b"),
    )

    return fig


def get_graph_info(data, metric, entity_name):
    if metric == "revenue":
        return data[data["entity_name"] == entity_name].sort_values(
            by="revenue", ascending=False
        )
    else:
        return data[data["entity_name"] == entity_name].sort_values(
            by="release_date", ascending=True
        )
