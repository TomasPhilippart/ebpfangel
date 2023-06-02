#!/usr/bin/python3

#   DISCLAIMER
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import os
import re
import glob
import numpy as np
import pandas as pd


# time period to compute the rate of event
# 1e9 nanoseconds = 1 second
TIME_PERIOD = 1e9

# TYPE_NAMES = ['open', 'create', 'delete', 'encrypt']
TYPE_NAMES = ['O', 'C', 'D', 'E']

# PID offset (to avoid duplicated PIDs across detector runs)
PID_OFFSET = 1e4

LOGDIR  = '../logs/'
DATADIR = '../data/'


def counts(df):
    # group by PID, TYPE and PERIOD
    ts = df['TS']
    df1 = df.assign(PERIOD=np.trunc((ts - ts[0]) / TIME_PERIOD))
    df1.drop(columns=['TS', 'FLAG', 'OPEN', 'CREATE', 'DELETE', 'ENCRYPT', 'FILENAME'], inplace=True)

    # count the number of event grouped by type, period and PID and move TYPE to column
    grouped = df1.groupby(['TYPE', 'PERIOD', 'PID']).agg(['count','sum']).unstack(level='TYPE', fill_value=0)

    # aggregate over time period (max per period + total)
    aggregated = grouped.groupby(level='PID').agg(['max','sum'])

    # rename levels/columns (skip 'PATTERN')
    aggregated.columns = aggregated.columns.to_flat_index()
    aggregated.rename(columns={col: '_'.join(col[1:]) for col in aggregated.columns}, inplace=True)

    # sum the number of pattern matches across events
    pattern_max = re.compile("^sum_\w+_max$")
    pattern_sum = re.compile("^sum_\w+_sum$")
    pattern_max_cols = [col for col in aggregated.columns if pattern_max.match(col)]
    pattern_sum_cols = [col for col in aggregated.columns if pattern_sum.match(col)]
    aggregated['P_max'] = aggregated[pattern_max_cols].sum(axis=1)
    aggregated['P_sum'] = aggregated[pattern_sum_cols].sum(axis=1)
    aggregated.drop(columns=pattern_max_cols + pattern_sum_cols, inplace=True)

    # strip "count_" from columns starting with count
    aggregated.rename(columns={col: col[6:] for col in aggregated.columns if col.startswith('count')}, inplace=True)

    return aggregated


def sequences(df):
    df1 = df.drop(columns=['FLAG', 'PATTERN', 'OPEN', 'CREATE', 'DELETE', 'ENCRYPT', 'FILENAME'])
    
    # count the number of event type sequences (length 3)
    df1['NEXT'] = df1.groupby(['PID'])['TYPE'].transform(lambda col: col.shift(-1, fill_value='X'))
    df1['AFTER'] = df1.groupby(['PID'])['TYPE'].transform(lambda col: col.shift(-2, fill_value='X'))   
    df1['SEQUENCE'] = df1[['TYPE', 'NEXT', 'AFTER']].apply(lambda row: ''.join(row.values.astype(str)), axis=1)

    aggregated = df1.groupby(['PID', 'SEQUENCE'])['TS'].agg('count').unstack(level='SEQUENCE', fill_value=0)

    # drop dummy sequences (containing X)
    aggregated.drop(columns=[col for col in aggregated.columns if 'X' in col], inplace=True)

    return aggregated


def main():
    # process logs in training and testing directories
    for dir in next(os.walk(LOGDIR))[1]:
        logs = glob.glob(LOGDIR + dir + '/*.csv')

        # PID collision fix (offset)
        df_arr = []
        for i,log in enumerate(logs):
            df = pd.read_csv(log)
            df['PID'] = df['PID'].map(lambda x: x + i * PID_OFFSET)
            # df['FILE'] = log
            df_arr.append(df)
        
        df = pd.concat(df_arr, ignore_index=True, verify_integrity=True)

        df['TYPE'].replace([0,1,2,3], TYPE_NAMES, inplace=True)

        c = counts(df)
        s = sequences(df)

        combined = pd.concat([c, s], axis=1)
        pd.set_option('display.max_rows', None)
        # print(combined)

        # save to csv
        combined.to_csv(DATADIR + dir + '_data.csv')


if __name__ == '__main__':
    main()
