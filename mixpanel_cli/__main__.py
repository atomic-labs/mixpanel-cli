#! python
import argparse
import io
import json
import logging
import pandas as pd
import sys

from pprint import pprint

from . import engage, events, export, funnel, retention

def events_get(args):
    print(events.events(args.event, args.type, args.unit, args.interval,
                        "csv" if args.csv else "json"))

def events_top(args):
    print(events.top(args.type, args.limit))

def events_names(args):
    print(events.names(args.type, args.limit))

def export_data(args):
    print(export.export(args.from_date, args.to_date, args.event, args.where,
                        args.bucket))

def funnel_list(args):
    print("\n".join(["%s\t%s" % (f["funnel_id"], f["name"]) for f in funnel.list()]))

def funnel_show(args):
    funnel_data = funnel.funnel(args.funnel_id)
    if args.csv:
        dates = funnel_data["meta"]["dates"]
        columns = [step["event"] for step in
                   funnel_data["data"][dates[0]]["steps"]]
        df = pd.DataFrame(columns=columns, index=dates)
        for date in funnel_data["meta"]["dates"]:
            for step in funnel_data["data"][date]["steps"]:
                df.loc[date, step["event"]] = step["count"]

        buf = io.StringIO()
        df.to_csv(buf, args.fs, index_label="week")
        buf.seek(0)
        print(buf.read())
    else:
        print(json.dumps(funnel_data))

def engage_list(args):
    pprint(engage.list(where=args.where, session_id=args.session_id,
                         page=args.page))

def retention_data(args):
    data = retention.retention(args.from_date, args.to_date,
                               retention_type=args.type,
                               born_event=args.born_event, event=args.event,
                               born_where=args.born_where, where=args.where,
                               interval=args.interval,
                               interval_count=args.interval_count,
                               unit=args.unit, on=args.on, limit=args.limit)

    if args.csv:
        dates = sorted(data.keys())
        columns = range(args.interval_count + 1)
        df = pd.DataFrame(columns=columns, index=dates)
        for date in dates:
            row = data[date]["counts"]
            for i in range(len(row)):
                df.loc[date, i] = row[i]

        buf = io.StringIO()
        if args.unit is None:
            if args.interval is None:
                label = "day"
            else:
                label = "%d days" % args.interval
        else:
            label = args.unit

        df.to_csv(buf, args.fs, index_label=label)
        buf.seek(0)
        print(buf.read())
    else:
        print(json.dumps(data))

if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser(description="Retrieve Mixpanel data")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="verbose logging output", action="store_true")
    subparsers = parser.add_subparsers(title="subcommands")
    #
    # Events
    #
    p_events = subparsers.add_parser("events", help="Query events")
    sp_events = p_events.add_subparsers(title="events subcommands")
    p_event_get = sp_events.add_parser("get", help="Get unique, total, or "
                                       "average data for a set of events over "
                                       "the last N days, weeks, or months.")
    p_event_get.add_argument("--event", "-e", action="append", required=True,
                             help="The event that you wish to get data for. "
                             "This argument may be included multiple times")
    p_event_get.add_argument("--type", "-t", required=True,
                             choices=("general", "unique", "average"),
                             help="The analysis type you would like to get "
                             "data for - such as general, unique, or average "
                             "events.")
    p_event_get.add_argument("--unit", "-u", required=True,
                             choices=("minute", "hour", "day", "week", "month"),
                             help="Determines the level of granularity of the "
                             "data you get back. Note that you cannot get "
                             "hourly uniques.")
    p_event_get.add_argument("--interval", "-i", required=True, type=int,
                             help="The number of \"units\" to return data for.")
    p_event_get.add_argument("--csv", action="store_true",
                             help="Print output in CSV format")
    p_event_get.set_defaults(func=events_get)
    p_event_top = sp_events.add_parser("top", help="Get the top events for "
                                       "today, with their counts and the "
                                       "normalized percent change from "
                                       "yesterday.")
    p_event_top.add_argument("type", choices=("general", "unique", "average"),
                             help="The analysis type you would like to get "
                             "data for - such as general, unique, or average "
                             "events.")
    p_event_top.add_argument("--limit", "-l", type=int, help="The maximum "
                             "number of events to return. Defaults to 100. The "
                             "maximum this value can be is 100.")
    p_event_top.set_defaults(func=events_top)
    p_event_names = sp_events.add_parser("names", help="Get a list of the most "
                                         "common events over the last 31 days.")
    p_event_names.add_argument("type", choices=("general", "unique", "average"),
                               help="The analysis type you would like to get "
                               "data for - such as general, unique, or average "
                               "events.")
    p_event_names.add_argument("--limit", "-l", type=int, help="The maximum "
                               "number of events to return. Defaults to 255.")
    p_event_names.set_defaults(func=events_names)

    #
    # Engage
    #
    p_engage = subparsers.add_parser("engage", help="Gets user data")
    p_engage.add_argument("-w", "--where", type=str, help="An expression to "
                          "filter people by. See the expression section.")
    p_engage.add_argument("-p", "--page", type=int, help="Which page of the "
                          "results to retrieve. Pages start at zero. If the "
                          "\"page\" parameter is provided, the session_id "
                          "parameter must also be provided.")
    p_engage.add_argument("-s", "--session_id", type=str, help="A string id "
                          "provided in the results of a previous query. Using "
                          "a session_id speeds up api response, and allows "
                          "paging through results.")
    p_engage.set_defaults(func=engage_list)

    #
    # Export
    #
    p_export = subparsers.add_parser("export", help="Export a date range")
    p_export.add_argument("from_date", help="The date in yyyy-mm-dd format "
                          "from which to begin querying for the event from. "
                          "This date is inclusive.")
    p_export.add_argument("to_date", help="The date in yyyy-mm-dd format "
                          "from which to stop querying for the event from. "
                          "This date is inclusive.")
    p_export.add_argument("--event", "-e", action="append",
                          help="Limit data to certain events. This argument "
                          "may be included multiple times")
    p_export.add_argument("--where", "-w", help="An expression to filter "
                          "events by. See the expression section on the main "
                          "data export API page.")
    p_export.add_argument("--bucket", "-b", help="[Platform] - the specific "
                          "data bucket you would like to query.")
    p_export.set_defaults(func=export_data)

    #
    # Funnel
    #
    p_funnel = subparsers.add_parser("funnel", help="Perform actions on funnels")
    sp_funnel = p_funnel.add_subparsers(title="funnel subcommands")
    p_funnel_list = sp_funnel.add_parser("list", help="Get the names and funnel_ids of your funnels.")
    p_funnel_list.set_defaults(func=funnel_list)
    p_funnel_show = sp_funnel.add_parser("show", help="Show the data in one funnel")
    p_funnel_show.add_argument("funnel_id", type=int, help="The ID of the funnel to display, returned by funnel list")
    p_funnel_show.add_argument("--csv", action="store_true",
                               help="Print output in CSV format")
    p_funnel_show.add_argument("--fs", type=str, default=",",
                               help="Field separator to use when printing CSV "
                               "output. Defaults to ','.")
    p_funnel_show.set_defaults(func=funnel_show)

    #
    # Retention
    #
    p_retention = subparsers.add_parser("retention",
                                        help="Get cohort analysis.")
    p_retention.add_argument("from_date", type=str,
                             help="The date in yyyy-mm-dd format from which to "
                             "begin generating cohorts from. This date is inclusive.")
    p_retention.add_argument("to_date", type=str,
                             help="The date in yyyy-mm-dd format from which to "
                             "stop generating cohorts from. This date is inclusive.")
    p_retention.add_argument("--type", "-t", type=str,
                             choices=(None, "birth", "compounded"),
                             help="Must be either 'birth' or 'compounded'. "
                             "Defaults to 'birth'.")
    p_retention.add_argument("--born_event", "-b", type=str,
                             help="The first event a user must do to be "
                             "counted in a birth retention cohort. Required "
                             "when retention_type is 'birth'; ignored otherwise.")
    p_retention.add_argument("--event", "-e", type=str,
                             help="The event to generate returning counts for. "
                             "Applies to both birth and compounded retention. "
                             "If not specified, we look across all events.")
    p_retention.add_argument("--born_where", type=str,
                             help="An expression to filter born_events by. See "
                             "the expression section.")
    p_retention.add_argument("--where", "-w", type=str,
                             help="An expression to filter the returning "
                             "events by. See the expression section.")
    p_retention.add_argument("--interval", "-i", type=int,
                             help="The number of days you want your results "
                             "bucketed into. The default value is 1 or "
                             "specified by unit.")
    p_retention.add_argument("--interval_count", "-c", type=int, default=1,
                             help="The number of intervals you want; defaults "
                             "to 1.")
    p_retention.add_argument("--unit", "-u", type=str,
                             choices=(None, "day", "week", "month"),
                             help="This is an alternate way of specifying "
                             "interval and can be 'day', 'week', or 'month'.")
    p_retention.add_argument("--on", type=str,
                             help="The property expression to segment the "
                             "second event on. See the expression section.")
    p_retention.add_argument("--limit", "-l", type=int,
                             help="Return the top limit segmentation values. "
                             "This parameter does nothing if 'on' is not specified.")
    p_retention.add_argument("--csv", action="store_true",
                             help="Print output in CSV format")
    p_retention.add_argument("--fs", type=str, default=",",
                               help="Field separator to use when printing CSV "
                               "output. Defaults to ','.")
    p_retention.set_defaults(func=retention_data)

    #
    # Handle input
    #

    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose
                               else logging.WARN))

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(2)

    args.func(args)
