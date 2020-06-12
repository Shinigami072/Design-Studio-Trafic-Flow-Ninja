$count = $args.Count

pipenv run python -m client $args[$count-2] $args[$count-1]