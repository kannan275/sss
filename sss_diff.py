import sss_filenames
import csv
import os

NEWER_DATE_AND_TIME = "Results/20201012-222853"
OLDER_DATE_AND_TIME = "Results/20200930-122044"
TICKER_INDEX        = 0
MOVEMENT_THRESHOLD  = 3 # Alert only for tickers which have moved more than a certain amount of positions

older_filenames_list = sss_filenames.create_filenames_list(OLDER_DATE_AND_TIME)
newer_filenames_list = sss_filenames.create_filenames_list(NEWER_DATE_AND_TIME)
diff_filenames_list  = sss_filenames.create_filenames_list('Results/diff'+'_new'+NEWER_DATE_AND_TIME.replace('Results/','_')+'_old'+OLDER_DATE_AND_TIME.replace('Results/','_'))


if len(older_filenames_list) != len(newer_filenames_list):
    raise Exception("Different Lengths of lists - Unacceptable")


def get_row_index(ticker, rows):
    index = 0
    for row in rows:
        if ticker == row[TICKER_INDEX]:
            return index
        index += 1
    return -1


for index in range(len(newer_filenames_list)):
    output_csv_rows = [['ticker','change','from','to']]
    print("\n{:20}:\n==========================================================".format(newer_filenames_list[index]))

    # 1st, Read the Older File, which will be the reference:
    older_rows = []
    with open(older_filenames_list[index], mode='r', newline='') as engine:
        reader = csv.reader(engine, delimiter=',')
        row_index = 0
        for row in reader:
            if row_index == 0:
                row_index += 1
                continue
            else:
                older_rows.append(row)
                row_index += 1

    # 2nd, read the Newer File and check if (and where) each line appears in the Older file (if at all)
    newer_rows = []
    with open(newer_filenames_list[index], mode='r', newline='') as engine:
        reader = csv.reader(engine, delimiter=',')
        row_index = 0
        for row in reader:
            if row_index == 0:
                row_index += 1
                continue
            else:
                newer_rows.append(row)
                ticker = row[TICKER_INDEX]
                row_index_in_older_file = get_row_index(ticker, older_rows)
                if row_index_in_older_file >= 0:
                    if abs(row_index_in_older_file - (row_index-1)) > MOVEMENT_THRESHOLD:
                        print("ticker {:10}: {:2} positions change from {:3} to {:3}".format(ticker, row_index_in_older_file-(row_index-1), row_index_in_older_file, (row_index-1)))
                        output_csv_rows.append([ticker, row_index_in_older_file-(row_index-1), row_index_in_older_file, (row_index-1)])
                else:
                    print("ticker {:10}: appears at position {:2} (new)".format(ticker, row_index-1))
                    output_csv_rows.append([ticker, 'new', 'new', (row_index - 1)])
                row_index += 1

    # 3rd, scan for Older File rows which do not appear in the Newer files anymore:
    row_index = 0
    for row in older_rows:
        ticker = row[TICKER_INDEX]
        row_index_in_newer_file = get_row_index(ticker, newer_rows)
        if row_index_in_newer_file < 0:
            print("ticker {:10}: disappeared from position {:2} (removed)".format(ticker, row_index))
            output_csv_rows.append([ticker, 'removed', row_index, 'removed'])
        row_index += 1
    # Write results to CSV (if any changes detected):
    if len(output_csv_rows) > 1:
        os.makedirs(os.path.dirname(diff_filenames_list[index]), exist_ok=True)
        with open(diff_filenames_list[index], mode='w', newline='') as engine:
            writer = csv.writer(engine)
            writer.writerows(output_csv_rows)
