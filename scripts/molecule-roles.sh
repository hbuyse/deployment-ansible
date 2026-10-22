#!/usr/bin/env bash
#
# Print the roles to test with Molecule, as a JSON array, for the files listed on the standard input (one path per
# line, relative to the root of the repository):
#   - the roles with a molecule/ directory that contain a changed file,
#   - the roles with a molecule/ directory that depend on one of them (meta/main.yml), directly or not,
#   - all of them when a file shared by the scenarios changed (molecule/shared/, group_vars/, requirements...),
#   - only jq, as a smoke test, when only the workflow changed.
#
# Used by .github/workflows/molecule.yml, usage: git diff --name-only <base> <head> | scripts/molecule-roles.sh

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

shared='^(molecule/|group_vars/|lookup_plugins/|requirements[^/]*$|ansible\.cfg$|scripts/molecule-roles\.sh$)'
workflow='^\.github/workflows/molecule\.yml$'

declare -A changed=()
all=false
smoke=false

while IFS= read -r path; do
    if [[ "${path}" =~ ${shared} ]]; then
        all=true
    elif [[ "${path}" =~ ${workflow} ]]; then
        smoke=true
    elif [[ "${path}" =~ ^roles/([^/]+)/ ]]; then
        changed["${BASH_REMATCH[1]}"]=1
    fi
done

has_scenario() {
    [ -d "roles/$1/molecule" ]
}

if "${all}"; then
    for dir in roles/*/molecule; do
        role="${dir#roles/}"
        changed["${role%/molecule}"]=1
    done
fi

# Add the dependents of the roles, until there are no more
grew=true
while "${grew}"; do
    grew=false
    for meta in roles/*/meta/main.yml; do
        [ -f "${meta}" ] || continue
        role="${meta#roles/}"
        role="${role%/meta/main.yml}"
        [ -z "${changed[${role}]:-}" ] || continue
        for dependency in "${!changed[@]}"; do
            if grep -Eq "^[[:space:]]*-[[:space:]]*(role:[[:space:]]*)?[\"']?${dependency}[\"']?[[:space:]]*$" "${meta}"; then
                changed["${role}"]=1
                grew=true
                break
            fi
        done
    done
done

roles=()
for role in "${!changed[@]}"; do
    has_scenario "${role}" && roles+=("${role}")
done

if [ ${#roles[@]} -eq 0 ] && "${smoke}"; then
    roles=(jq)
fi

if [ ${#roles[@]} -eq 0 ]; then
    echo '[]'
else
    printf '%s\n' "${roles[@]}" | sort | jq --raw-input . | jq --slurp --compact-output .
fi
