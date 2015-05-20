#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

from klab.process.file_manager import read_df_from_file, write_df_to_file
from klab.process.derived_info import standardize_column_headers

KEY_COL_NAME = 'key_col'

SOUTH_LAT_LOW = 65.5
SOUTH_LAT_HIGH = 69
SOUTH_LON_LOW = 66.5
SOUTH_LON_HIGH = 76.5
NORTH_LAT_LOW = 61.8
NORTH_LAT_HIGH = 66
NORTH_LON_LOW = 58
NORTH_LON_HIGH = 68


def add_wap_region_column(df, lat_col, lon_col):
    df['wap_region'] = 'None'
    df.loc[(abs(df[lat_col]) >= SOUTH_LAT_LOW) & (abs(df[lat_col]) <= SOUTH_LAT_HIGH) &
           (abs(df[lon_col]) >= SOUTH_LON_LOW) & (abs(df[lon_col]) <= SOUTH_LON_HIGH), ['wap_region']] = 'South'
    df.loc[(abs(df[lat_col]) >= NORTH_LAT_LOW) & (abs(df[lat_col]) <= NORTH_LAT_HIGH) &
           (abs(df[lon_col]) >= NORTH_LON_LOW) & (abs(df[lon_col]) <= NORTH_LON_HIGH), ['wap_region']] = 'North'


def add_year_month_column(df, col_name):
    df['year_month'] = df[col_name].apply(lambda x: str(x)[:7])
    return df


# def add_depth_column(df, depth_col):
# df['depth'] = 'None'
#     df.loc[(df[depth_col] > -2) & (df[depth_col] <= 25), ['depth']] = '0-25'
#     df.loc[(df[depth_col] > 25) & (df[depth_col] <= 50), ['depth']] = '25-50'
#     df.loc[(df[depth_col] > 50) & (df[depth_col] <= 110), ['depth']] = '50-110'
#     return df


def process_file(filename, lat_col, lon_col, date_col, depth_col, key_col):
    df = read_df_from_file('/shared_projects/PLTER/annual_cruise/' + filename)
    standardize_column_headers(df)
    df.rename(columns={key_col: KEY_COL_NAME}, inplace=True)
    add_wap_region_column(df, lat_col, lon_col)
    add_year_month_column(df, date_col)
    df2 = df[df['year_month'].str.startswith('2') &  # years >= 2000
             (df[depth_col] > -5) & (df[depth_col] < 20) &  # 0-20m depth
             (df['wap_region'] != 'None') &  # only specific regions
             (df[KEY_COL_NAME] > -990)  # remove the 'wacky' values
             ]
    df2['year'] = df['year_month'].apply(lambda x: x[:4])
    return pd.DataFrame(df2)


def do_it(filename, lat_col, lon_col, date_col, depth_col, key_col, out_file=None):
    path = '/shared_projects/PLTER/annual_cruise/'
    if not out_file:
        out_file = filename
    df = process_file(filename, lat_col, lon_col, date_col, depth_col, key_col)
    write_df_to_file(df, path + 'cleaned/' + out_file)

    d2 = df[['year', 'wap_region', KEY_COL_NAME]]

    d3 = pd.DataFrame(d2.groupby(['year', 'wap_region']).agg(['mean', 'sem']))
    d3.reset_index(inplace=True)
    d3.columns = ['year', 'wap_region', 'mean', 'sem']

    pt = pd.pivot_table(d3, index=['year', 'wap_region'])

    d4 = pt.unstack()
    d4.fillna(0, inplace=True)
    d4.columns = d4.columns.get_level_values(1)
    d4.reset_index(inplace=True)
    write_df_to_file(d4, path + 'cleaned/final_' + out_file)


if __name__ == '__main__':
    lat_col = 'latitude_(º)'
    lon_col = 'longitude_(º)'
    date_col = 'datetime_gmt'
    depth_col = 'depth_(m)'

    filename = 'Primary_Production_41.csv'
    key_col = 'primary_production_(mg/m³/day)'
    do_it(filename, lat_col, lon_col, date_col, depth_col, key_col)

    filename = 'Chlorophyll_24.csv'
    key_col = 'chlorophyll_(mg/m³)'
    do_it(filename, lat_col, lon_col, date_col, depth_col, key_col)

    filename = 'Chlorophyll_24.csv'
    out_file = 'Phaeopigment_24.csv'
    key_col = 'phaeopigment_(mg/m³)'
    do_it(filename, lat_col, lon_col, date_col, depth_col, key_col, out_file)

    filename = 'Bacteria_48.csv'
    key_col = 'abundance'
    do_it(filename, lat_col, lon_col, date_col, depth_col, key_col)

    filename = 'Dissolved_Oxygen_50.csv'
    key_col = 'o2_(ml/l)'
    lat_col = 'lat_dec_(º)'
    lon_col = 'lon_dec_(º)'
    do_it(filename, lat_col, lon_col, date_col, depth_col, key_col)

    # filename = 'HPLC_Pigments_42.csv'
    # do_it(filename, 'latitude_(º)', 'longitude_(º)')
    #
    # filename = 'Particulate_Organic_Carbon_Nitrogen_36.csv'
    # do_it(filename, 'latitude_(º)', 'longitude_(º)')
    #
    # filename = 'Dissolved_Inorganic_Nutrients_27.csv'
    # do_it(filename, 'latitude_(º)', 'longitude_(º)')
    #
    # filename = 'Zooplankton_Density_199.csv'  # no north?
    # do_it(filename, 'latitudestart_(º)', 'longitudestart_(º)')
    #
    # filename = 'Zooplankton_Density_212.csv'
    # do_it(filename, 'latitudestart_(º)', 'longitudestart_(º)')
