# aws-org-tree

Uses AnyTree to render and export the complete organizational structure.

## Basics

<details>
<summary>
Print a text tree representation of the organization showing just the IDs. (Click to show output.)

```bash
aws-org-tree
```

or

```bash
aws-org-tree text-tree
```

</summary>

Result:

```text
r-auh0
├── 897617218731
├── 975072629527
├── 480783779961
├── 139442570134
├── ou-auh0-udicosld
│   └── 345132479590
├── ou-auh0-5qqlm6wn
│   └── 749430203777
└── ou-auh0-p5cmxwe9
    ├── 933189656188
    ├── 638726906110
    ├── 423811555754
    └── 192985681585
```
</details>

<details>
<summary>
Print a JSON tree representation of the same with all attributes. (Click to show output.)

```bash
aws-org-tree json-tree | jq
```
</summary>

```json
{
  "Properties": {
    "Id": "r-auh0",
    "Arn": "arn:aws:organizations::480783779961:root/o-webyrpj5yp/r-auh0",
    "Name": "Root",
    "PolicyTypes": [
      {
        "Type": "SERVICE_CONTROL_POLICY",
        "Status": "ENABLED"
      }
    ],
    "Type": "ROOT"
  },
  "name": "r-auh0",
  "children": [
    {
      "Properties": {
        "Id": "897617218731",
        "Type": "ACCOUNT",
        "Arn": "arn:aws:organizations::480783779961:account/o-webyrpj5yp/897617218731",
        "Email": "...",
        "Name": "...",
        "Status": "ACTIVE",
        "JoinedMethod": "CREATED",
        "JoinedTimestamp": "2021-09-29T17:00:35.949000+02:00"
      },
      "name": "897617218731"
    },
    {
      "Properties": {
        "Id": "975072629527",
        "Type": "ACCOUNT",
        "Arn": "arn:aws:organizations::480783779961:account/o-webyrpj5yp/975072629527",
        "Email": "...",
        "Name": "...",
        "Status": "ACTIVE",
        "JoinedMethod": "CREATED",
        "JoinedTimestamp": "2021-09-27T17:37:30.689000+02:00"
      },
      "name": "975072629527"
    },
```
</details>

<details>
<summary>
Print a flat JSON representation of the same with all attributes. (Click to show output.)

```bash
aws-org-tree json-flat | jq
```
</summary>

```json
[
  {
    "Id": "r-auh0",
    "Arn": "arn:aws:organizations::480783779961:root/o-webyrpj5yp/r-auh0",
    "Name": "Root",
    "PolicyTypes": [
      {
        "Type": "SERVICE_CONTROL_POLICY",
        "Status": "ENABLED"
      }
    ],
    "Type": "ROOT",
    "Parent": null
  },
  {
    "Id": "897617218731",
    "Type": "ACCOUNT",
    "Arn": "arn:aws:organizations::480783779961:account/o-webyrpj5yp/897617218731",
    "Email": "...",
    "Name": "...",
    "Status": "ACTIVE",
    "JoinedMethod": "CREATED",
    "JoinedTimestamp": "2021-09-29T17:00:35.949000+02:00",
    "Parent": "r-auh0"
  },
  {
    "Id": "975072629527",
    "Type": "ACCOUNT",
    "Arn": "arn:aws:organizations::480783779961:account/o-webyrpj5yp/975072629527",
    "Email": "...",
    "Name": "...",
    "Status": "ACTIVE",
    "JoinedMethod": "CREATED",
    "JoinedTimestamp": "2021-09-27T17:37:30.689000+02:00",
    "Parent": "r-auh0"
  },
```
</details>

## Advanced uses

The json-flat output format can be easily loaded into an SQL database. There one can build a ragged hierarchy bridge table that permits the organizational structure to be queried using SQL.

This allows you to answer questions such as:

* How many accounts are in a given OU (organizational unit)?
* A stack set has OUTDATED and INOPERABLE instances. Which OU are those accounts in?

See [Building a hierarchy bridge table](building-a-hierarchy-bridge-table.md) for a way to do this using SQLite.

## Solution Notes

The OrgTree class traverses the organization by recursively listing the children. Organizational units can contain other organizational units and accounts. Accounts are leaves.

[Boto3](https://github.com/boto/boto3) is used for all API calls to AWS Organizations.

[AnyTree](https://github.com/c0fec0de/anytree) is used to to store and operate on the internal tree data structure.

[Logdecorator](https://github.com/sighalt/logdecorator) provides the logging while keeping the business logic clean.

[CollatorClient](https://github.com/iainelder/boto-collator-client) is used to abstract over the paginated API responses.

## Trees in Python

A survey article on making data tree in Python:

* https://medium.com/swlh/making-data-trees-in-python-3a3ceb050cfd

Python tree libraries:

* https://treelib.readthedocs.io/en/latest/
* https://github.com/c0fec0de/anytree
* https://github.com/joowani/binarytree
* https://wiki.python.org/moin/PythonGraphApi

## Other solutions

In October 2021 AWS announced a new feature of the Organizations console called "Exporting all AWS account details for your organization".

It provides less detail than the output of aws-org-tree.

https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_export.html?icmpid=docs_orgs_console

# TODO

* Refactor the code done quick

   * Move methods on OrgTree to Output classes
   * Replace OrgTree class with a build function that returns an AnyTree
   * Class for each of the org things
   * NodeMixin in a class that also accepts a selector for the attributes to show

* Moto for generating aribtrary org trees for testing
* Account tags
* Create proper organization class with the attributes for the things you would expect: management account, org ID, root, ...
