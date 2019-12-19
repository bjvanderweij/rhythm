#!/bin/bash

# Each line in the input is a path to a score.
# Convert this score to *one line*, containing a recip representation with newlines replaced by spaces

echo -n '' > $1

while read p; do
    # Extract the first spine
    first_spine=$(extract -f 1 < $p)
    # Convert to recip representation, replace **kern by **recip (unnecessary)
    recip=$(echo "$first_spine" | humsed '/^[^=]/s/[^][0-9.r ]//g; s/^$/./' | sed 's/**kern/**recip/')
    # Filter out recip events, replace newlines by spaces, append to $1
    tokens=$(echo "$recip" | grep -E '^([][0-9=]|\*M[0-9]+\/[0-9]+)'  | tr '\n' ' ')
    # Obtain filename
    filename=$(basename $p .krn)
    # Append filename and recip line to file
    printf "%s %s\n" "$filename" "$tokens" >> $1
done < /dev/stdin
