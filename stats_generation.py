from datetime import timedelta, datetime
from textwrap import fill
import matplotlib.pyplot as plt
import pandas as pd


def read_data(json_path, date_start):
    """Return a week's worth of data from a JSON file and return it as a dataframe"""
    date_end = date_start + timedelta(days=7)  # Set end date a week from the start date
    df = pd.read_json(json_path, lines=True)  # Convert to dataframe
    return df.loc[(df['Date'] >= date_start) & (df['Date'] <= date_end)]


def generate_stats(json_path, date_start=datetime.now() - timedelta(days=7)):
    """Calculates metrics for Sightdata report

        Parameters:
        json_path (String): Path to JSON document
        date_start (date)): Starting date of data. Default is a week prior to current date

        Returns:
        list: Each row represents one module:
            column 1: ['Exclusion Zone Detection', no. of detected breaches, no. of close proximity warnings,
                percent of compliant events, 'Detected Breaches', 'Close Proximity Warnings', 'Percent Compliant']
            column 2: ['Loose Object Detection', total no. of loose objects detected, no. of loose objects remaining,
                'Loose Objects Detected', 'Objects remaining']
       """
    data = read_data(json_path, date_start)  # Read a week's worth of data

    # Calculate metrics
    # No. of detected exclusion zone breaches
    ez_breaches = data[(data.Module == 'Exclusion Zone Detection') & (data.Value == 'Breach')].count()['Value']
    # No. of detected exclusion zone close proximity warnings
    ez_close = data[(data.Module == 'Exclusion Zone Detection') & (data.Value == 'Close Proximity')].count()['Value']
    # No. of detected exclusion zone compliant events
    ez_compliant = data[(data.Module == 'Exclusion Zone Detection') & (data.Value == 'Compliant')].count()['Value']
    # No. of total loose objects detected
    lod_total = data[(data.Module == 'Loose Object Detection')].count()['Value']
    # No. of current loose objects detected
    lod_current = data[(data.Module == 'Loose Object Detection') & (data.Value == 'Unresolved')].count()['Value']
    # ppe = data[(data.module == 'PPE Detection') & (data.value == 'Breach')].count()['value']
    # total_people = data[(data.module == 'PPE Detection')].count()['value']

    return [['Exclusion Zone Detection', str(ez_breaches), str(ez_close),
             str(round((ez_compliant * 100) / (ez_breaches + ez_close + ez_compliant))), 'Detected Breaches',
             'Close Proximity Warnings', 'Percent Compliant'],
            ['Loose Object Detection', str(lod_total), str(lod_current), 'Loose Objects Detected', 'Objects Remaining']]
    # ['PPE Detection', str(ppe), str(total_people), 'Detected Breaches', 'Total PPE Detected']]


def generate_graph(json_path, out_path, grouping='date', graph_type='bar',
                   date_start=datetime.now() - timedelta(days=7)):
    """Generate graphs for Sightdata report

            Parameters:
            json_path (String): Path to JSON document
            out_path (String): Location to save graphs
            grouping: x-axis of graph (date, hour, area, camera). Default is 'date'.
            graph_type: type of graph (bar, line, barh). Default is 'bar'.
            date_start (date)): Starting date of data. Default is a week prior to current date

            Returns:
            None
           """
    # Optional colour settings for graphs
    # sightdata_chart_colours = ['#3595f5', '#e45454', '#fcb41c']  # Red Blue Yellow
    sightdata_chart_colours_2 = ['#000000', '#ef9511', '#767171', '#ffc000']  # Black Gold Grey Yellow

    data = read_data(json_path, date_start)  # Read data
    data_breaches = data.loc[(data.Value == 'Breach') | (data.Value == 'Unresolved')]  # Extract unresolved incidents

    # Group data
    if grouping == 'camera' or grouping == 'area':
        # Group data by camera/area
        grouped_data = data_breaches.groupby(['Camera', 'Module'],
                                             sort=True).count()['Value'].unstack('Module', fill_value=0)

    elif grouping == 'hour':
        # Group data by hour
        grouped_data = data_breaches.groupby([pd.to_datetime(data_breaches['Date']).dt.hour, 'Module'],
                                             sort=True).count()['Value'].unstack('Module', fill_value=0)

        # Add any missing hours to data
        if len(grouped_data.index) < 24:
            idx = pd.RangeIndex(0, 24)
            grouped_data = grouped_data.reindex(idx, fill_value=0)

        grouped_data.index.names = ['Hour']  # Change index name

        # Change hour to hour : minute format
        replace_index = {}
        for x in grouped_data.index:
            replace_index[x] = '{}:00'.format(x)
        grouped_data = grouped_data.rename(index=replace_index)

        # Divide count so that it shows average no. of incidents per hour
        grouped_data = grouped_data.div(7).round(2)
        print(grouped_data)

    else:
        # Group data by date
        grouped_data = data_breaches.groupby([pd.to_datetime(data_breaches['Date']).dt.strftime('%d/%m/%Y'), 'Module'],
                                             sort=False).count()['Value'].unstack('Module', fill_value=0)

        # Sort and format dates
        grouped_data.index = pd.DatetimeIndex(grouped_data.index)

        # Add any missing dates to data
        if len(grouped_data.index) < 7:
            idx = pd.date_range(date_start, date_start + timedelta(days=7))
            grouped_data = grouped_data.reindex(idx, fill_value=0)

        grouped_data = grouped_data.sort_index()  # Sort index
        new_index = grouped_data.index.strftime('%d/%m')  # Formate date column to only show day and month
        grouped_data = grouped_data.rename(
            index=dict(zip(grouped_data.index.tolist(), new_index.tolist())))  # Replace index

    # Create graphs
    if graph_type == 'line':
        grouped_data.plot(color=sightdata_chart_colours_2, figsize=(28 / 2.54, 7 / 2.54))  # Plot data

        # Create legend
        labels = [fill(line, 20) for line in grouped_data.columns]  # Allow legend labels to wrap to next line
        plt.gca().legend(labels, loc='upper right', bbox_to_anchor=(-0.05, 1), title=None)  # Set position of legend
        plt.subplots_adjust(left=0.3, right=0.9)  # Set location of plot to leave space for legend

        # Set x-axis ticks to show each hour
        x = [i for i in range(0, 24)]  # Set no. of ticks
        labels = grouped_data.index.tolist()  # Get tick text
        plt.xticks(x, labels, rotation=45)  # Set x-axis ticks with tick text at a 45 degree angle
        plt.locator_params(axis='x', nbins=len(x) / 2)  # Show only every second hour tick
        plt.gca().set_axisbelow(True)  # Set grid below graph
        plt.gca().grid(axis='y')  # Turn on grid

    if graph_type == 'line2':
        grouped_data.plot(color=sightdata_chart_colours_2, figsize=(25 / 2.54, 5 / 2.54))  # Plot data

        # Shrink current axis's height by 20% on the bottom
        box = plt.gca().get_position()
        plt.gca().set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8])

        # Put a legend below current axis
        plt.gca().legend(loc='upper center', bbox_to_anchor=(0.5, -0.5), frameon=False, ncol=2)

        # Set x-axis ticks to show each hour
        x = [i for i in range(0, 24)]  # Set no. of ticks
        labels = grouped_data.index.tolist()  # Get tick text
        plt.xticks(x, labels, rotation=45)  # Set x-axis ticks with tick text at a 45 degree angle
        plt.locator_params(axis='x', nbins=len(x) / 2)  # Show only every second hour tick
        plt.gca().set_axisbelow(True)  # Set grid below graph
        plt.gca().grid(axis='y')  # Turn on grid

    elif graph_type == 'barh':
        grouped_data.plot(kind='barh', color=sightdata_chart_colours_2, figsize=(12 / 2.54, 9 / 2.54),
                          legend=False)  # Plot data
        plt.gca().invert_yaxis()  # Set so first area/camera is at top of graph
        plt.gca().set_axisbelow(True)  # Set grid below graph
        plt.gca().grid(axis='x')  # Turn on grid

    else:
        grouped_data.plot(kind='bar', color=sightdata_chart_colours_2, figsize=(12 / 2.54, 8 / 2.54),
                          legend=False)  # Plot data
        plt.xticks(rotation=45)  # Set x-axis ticks a 45 degree angle
        plt.gca().set_axisbelow(True)  # Set grid below graph
        plt.gca().grid(axis='y')  # Turn on grid

    ax = plt.gca()
    ax.spines['right'].set_visible(False)  # Hide right boarder
    ax.spines['top'].set_visible(False)  # Hide top boarder
    ax.spines['bottom'].set_visible(False)  # Hide bottom boarder
    ax.spines['left'].set_visible(False)  # Hide left boarder
    ax.tick_params(axis=u'both', which=u'both', length=0)
    ax.set(xlabel=None, ylabel=None)  # Hide x and y labels
    plt.savefig(out_path, bbox_inches="tight")  # Save figure
