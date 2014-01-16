#! python
import argparse
import io
import json
import logging
import pandas as pd
import sys

from pprint import pprint

from . import engage, export, funnel

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

if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser(description="Retrieve Mixpanel data")
    parser.add_argument("-v", "--verbose", dest="verbose",
                        help="verbose logging output", action="store_true")
    subparsers = parser.add_subparsers(title="subcommands")

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

    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose
                               else logging.WARN))

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(2)

    args.func(args)
