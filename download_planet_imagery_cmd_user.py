import getpass
from planet import Auth, Session, DataClient, OrdersClient, data_filter, order_request
import planet
from pprint import pprint
from zipfile import ZipFile
import json
import os
import asyncio
from datetime import datetime
from pathlib import Path
from pprint import pprint
from zipfile import ZipFile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import rasterio
from shapely.geometry import MultiPolygon, shape

# Get the user account name and password
# from the command line and environment,
# and store credentials in an Auth object
user = input("Username: ")
pw = getpass.getpass()
auth = Auth.from_login(user,pw)
auth.store()

## name the order
order_name = input("Order Name: ")

## insert path to roi geojson
ROI = input("Path to ROI: ")
roi = open(ROI)
roi = json.load(roi)

## insert temporal constraints YYYY-MM-DD
start_time = input("Start time (YYYY-MM-DD): ")
end_time = input("End time (YYYY-MM-DD): ")
output_folder = input("Output Directory Path: ")

try:
    os.path.exists(output_folder)
except:
    os.mkdir(output_folder)

def create_combined_filter(roi, time1, time2):
    """
    inputs:
    aoi (str) is path to geojson with bounds for imagery
    time1 (str) is start time YYYY-MM-DD
    time2 (str) is end time YYYY-MM-DD
    outputs:
    request json to download planet imagery
    """
    item_type = ['PSScene']

    ##Get time strings
    day_min = int(time1[-2:])
    month_min = int(time1[-5:-3])
    year_min = int(time1[0:4])
    day_max = int(time2[-2:])
    month_max = int(time2[-5:-3])
    year_max = int(time2[0:4])
    
    data_range_filter = data_filter.date_range_filter("acquired",
                                                      datetime(month=month_min,
                                                               day=day_min,
                                                               year=year_min),
                                                      datetime(month=month_max,
                                                               day=day_max,
                                                               year=year_max))
    clear_percent_filter = data_filter.range_filter('clear_percent',
                                                    None,
                                                    None,
                                                    90)
    
    geom_filter = data_filter.geometry_filter(roi)
    
    #combining aoi and time and clear percent filter
    combined_filter = data_filter.and_filter([geom_filter,
                                              clear_percent_filter,
                                              data_range_filter])
    return combined_filter

combined_filter = create_combined_filter(roi,
                                         start_time,
                                         end_time)
    
async def create_and_download(client, order_detail, directory):
    with planet.reporting.StateBar(state='creating') as reporter:
        order = await client.create_order(order_detail)
        reporter.update(state='created',
                        order_id=order['id'])
        await client.wait(order['id'],
                          callback=reporter.update_state)

    await client.download_order(order['id'],
                                directory,
                                progress_bar=True)

async def main():
    async with planet.Session() as sess:
        cl = sess.client('data')

        # Create the order request
        request = await cl.create_search(name='temp_search',
                                         search_filter=combined_filter,
                                         item_types=['PSScene'])
        items = cl.run_search(search_id=request['id'])
        item_list = [i async for i in items]
        # We can create a function to get the acquired dates for all of our search results
        def get_acquired_date(item):
            return item['properties']['acquired'].split('T')[0]
        
        acquired_dates = [get_acquired_date(item) for item in item_list]
        unique_acquired_dates = set(acquired_dates)
        # We can also list our Image IDs grouped based on Acquired Date
        def get_date_item_ids(date, all_items):
            """
            Get the item IDs for items with a specific acquired date.

            Args:
                date (str): The target acquired date in string format (e.g., '2023-06-27').
                all_items (list): A list of item dictionaries, each containing an 'id' field and 'acquired' field.

            Returns:
                list: A list of item IDs that have the specified acquired date.
            """
            return [i['id'] for i in all_items if get_acquired_date(i) == date]


        def get_ids_by_date(items):
            """
            Returns a dictionary mapping of acquired dates of the Image IDs to lists of item IDs.

            Args:
                items (list): A list of items.

            Returns:
                dict: A dictionary where the keys are acquired dates and the values are lists of item IDs.
            """
            acquired_dates = [get_acquired_date(item) for item in items]
            unique_acquired_dates = set(acquired_dates)

            ids_by_date = dict((d, get_date_item_ids(d, items))
                               for d in unique_acquired_dates)
            return ids_by_date
        
        ids_by_date = get_ids_by_date(item_list)
        ids = ids_by_date[list(unique_acquired_dates)[0]]
       
        cl = sess.client('orders')
        request = planet.order_request.build_request(name=order_name,
                                                     products=[planet.order_request.product(item_ids=ids,
                                                                                            product_bundle='analytic_udm2',
                                                                                            item_type='PSScene')
                                                    ],
                                                     tools=[planet.order_request.clip_tool(aoi=roi)]
                                                     )
       # Create and download the order
        order = await create_and_download(cl,
                                          request,
                                          output_folder)
if __name__ == '__main__':
    asyncio.run(main())

    
