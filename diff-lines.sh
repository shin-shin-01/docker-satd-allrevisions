#!/bin/sh
# diff-lines.sh
# Ref: Using git diff, how can I get added and modified lines numbers? - Stack Overflow - 
#      http://stackoverflow.com/questions/8259851/using-git-diff-how-can-i-get-added-and-modified-lines-numbers
path=
line=
while read; do
  esc=$'\033'
  if [[ "$REPLY" =~ ---\ (a/)?.* ]]; then
    continue
  elif [[ "$REPLY" =~ \+\+\+\ (b/)?([^[:blank:]]+).* ]]; then
    path=${BASH_REMATCH[2]}
  elif [[ "$REPLY" =~ @@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,[0-9]+)?\ @@.* ]]; then
    line=${BASH_REMATCH[2]}
  elif [[ "$REPLY" =~ ^($esc\[[0-9;]+m)*([\ +-]) ]]; then
    echo "$path:$line:$REPLY"
    if [[ "${BASH_REMATCH[2]}" != - ]]; then
      ((line++))
    fi
  fi
done
