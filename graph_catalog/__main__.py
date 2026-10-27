import argparse
import json
import sys
from .catalog import inspect_graph, check_mapping, _text


def main():
    parser = argparse.ArgumentParser(description="Inspect graphs or check a supplied mapping.")
    parser.add_argument("command", choices=("inspect", "check"))
    args = parser.parse_args()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            required = {"id", "graph"} if args.command == "inspect" else {"id", "left", "right", "anchors", "mapping"}
            if not isinstance(request, dict) or set(request) != required:
                raise ValueError("invalid request fields")
            request_id = _text(request["id"])
            if args.command == "inspect":
                result = {"id": request_id, **inspect_graph(request["graph"])}
            else:
                result = {"id": request_id, "valid": check_mapping(request["left"], request["right"], request["anchors"], request["mapping"])}
        except (ValueError, TypeError, UnicodeError):
            result = {"error": "invalid_request"}
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
