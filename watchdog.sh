#!/bin/zsh

SELF=${0:A}
CURRENT_DIR=${0:A:h}

declare -ga triggers

sort-triggers() {
  echo $(printf '%s\n' "$@" | sort -u)
}

watch-file-changes() {
  fswatch \
    --event Created \
    --event MovedFrom \
    --event MovedTo \
    --event Removed \
    --event Renamed \
    --event Updated \
    --exclude $CURRENT_DIR/\.git \
    --exclude $CURRENT_DIR/\.tox \
    --exclude \.isorted \
    --exclude __pycache__ \
    --exclude egg-info \
    --exclude tests/reports \
    --recursive \
    $CURRENT_DIR
}

on-file-change() {
  while true; do
    read file
    filter-change $file
    while read -t 2 file; do
      filter-change $file
    done
    run-triggers
  done
}

filter-change() {
  case $1 in
    $SELF)
      triggers+=(0-update-self)
      ;;
    $CURRENT_DIR/(pyproject\.toml|poetry\.lock|tox\.ini))
      triggers+=(1-run-tests)
      ;;
    $CURRENT_DIR/*.py)
      triggers+=(1-run-tests)
      ;;
  esac
}

run-triggers() {
  triggers=($(sort-triggers ${triggers[@]}))
  for trigger in $triggers; do
    $trigger
  done
  triggers=()
}

0-update-self() {
  triggers=("${triggers[@]:1}")
  echo "Running $0 ${triggers[@]} ..."
  exec $SELF "${triggers[@]}"
}

1-run-tests() {
  echo "Running tests ..."
  tox
}

echo "Watching file changes in $CURRENT_DIR ..."
watch-file-changes | on-file-change
