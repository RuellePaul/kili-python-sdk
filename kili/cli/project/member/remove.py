"""CLI's project member remove subcommand"""

from typing import Optional
import warnings
import click
from kili.cli.project.member.helpers import (
    check_exclusive_options,
    collect_members_from_csv,
    collect_members_from_emails,
    collect_members_from_project,
)


from kili.client import Kili
from kili.cli.common_args import Options


@click.command()
@Options.api_key
@Options.endpoint
@click.argument("emails", type=str, required=False, nargs=-1)
@click.option("--project-id", type=str, required=True, help="Id of the project to add members to")
@click.option(
    "--from-csv",
    "csv_path",
    type=click.Path(),
    help="path to a csv file with email in the first column",
)
@click.option(
    "--all",
    "all_members",
    type=bool,
    is_flag=True,
    default=False,
    help="Remove all users from project",
)
# pylint: disable=too-many-arguments
def remove_member(
    api_key: Optional[str],
    endpoint: Optional[str],
    emails: Optional[str],
    project_id: str,
    csv_path: Optional[str],
    all_members: bool,
):
    """Remove members from a Kili project

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member rm \\
            --project-id <project_id> \\
            john.doe@test.com
        ```
        ```
        kili project member rm \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv

        ```
        ```
        kili project member rm \\
            --project-id <project_id> \\
            --all
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)

    check_exclusive_options(csv_path, None, emails, all_members)

    if csv_path is not None:
        members_to_rm = collect_members_from_csv(csv_path, None)
    elif all_members:
        members_to_rm = collect_members_from_project(kili, project_id, None)
    else:
        members_to_rm = collect_members_from_emails(emails, None)

    count = 0
    existing_members = kili.project_users(project_id=project_id, disable_tqdm=True)
    existing_members = {
        member["user"]["email"]: member["id"] for member in existing_members if member["activated"]
    }

    for member in members_to_rm:
        email = member["email"]
        if email in existing_members.keys():
            kili.delete_from_roles(role_id=existing_members[email])
            count += 1
        else:
            warnings.warn(f"{email} is not an active member of the project.")

    print(f"{count} users have been successfully removed from project: {project_id}")