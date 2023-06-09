# aws-org-tree

Renders and exports the tree structure of an AWS organization.

## Basics

<details>
<summary>
Print a text tree representation of the organization showing just the IDs. (Click to show output.)

```bash
aws-org-tree
```

or

```bash
aws-org-tree --tree-format text-tree
```

</summary>

Result:

```text
r-p74l
├── 039444814027
├── ou-p74l-a2llanp8
└── ou-p74l-094nw8v7
    ├── 386884128156
    └── 466721047587
```
</details>

<details>
<summary>
Print a JSON tree representation of the same with all attributes. (Click to show output.)

```bash
aws-org-tree --tree-format json-tree
```
</summary>

```json
{
  "Properties": {
    "Id": "r-p74l",
    "Arn": "arn:aws:organizations::039444814027:root/o-p66trezrse/r-p74l",
    "Name": "Root",
    "PolicyTypes": [
      {
        "Type": "SERVICE_CONTROL_POLICY",
        "Status": "ENABLED"
      }
    ],
    "Type": "ROOT"
  },
  "name": "r-p74l",
  "children": [
    {
      "Properties": {
        "Id": "039444814027",
        "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/039444814027",
        "Email": "iain+awsroot+zcskbx@isme.es",
        "Name": "isme-root-zcskbx",
        "Status": "ACTIVE",
        "JoinedMethod": "INVITED",
        "JoinedTimestamp": "2023-06-08T12:14:55.704000+02:00",
        "Type": "ACCOUNT"
      },
      "name": "039444814027"
    },
    {
      "Properties": {
        "Id": "ou-p74l-a2llanp8",
        "Arn": "arn:aws:organizations::039444814027:ou/o-p66trezrse/ou-p74l-a2llanp8",
        "Name": "Sandbox",
        "Type": "ORGANIZATIONAL_UNIT"
      },
      "name": "ou-p74l-a2llanp8"
    },
    {
      "Properties": {
        "Id": "ou-p74l-094nw8v7",
        "Arn": "arn:aws:organizations::039444814027:ou/o-p66trezrse/ou-p74l-094nw8v7",
        "Name": "Security",
        "Type": "ORGANIZATIONAL_UNIT"
      },
      "name": "ou-p74l-094nw8v7",
      "children": [
        {
          "Properties": {
            "Id": "386884128156",
            "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/386884128156",
            "Email": "iain+awsroot+zcskbx+log-archive@isme.es",
            "Name": "Log Archive",
            "Status": "ACTIVE",
            "JoinedMethod": "CREATED",
            "JoinedTimestamp": "2023-06-08T12:15:24.407000+02:00",
            "Type": "ACCOUNT"
          },
          "name": "386884128156"
        },
        {
          "Properties": {
            "Id": "466721047587",
            "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/466721047587",
            "Email": "iain+awsroot+zcskbx+audit@isme.es",
            "Name": "Audit",
            "Status": "ACTIVE",
            "JoinedMethod": "CREATED",
            "JoinedTimestamp": "2023-06-08T12:15:15.815000+02:00",
            "Type": "ACCOUNT"
          },
          "name": "466721047587"
        }
      ]
    }
  ]
}
```
</details>

<details>
<summary>
Print a flat JSON representation of the same with all attributes. (Click to show output.)

```bash
aws-org-tree --tree-format json-flat | jq
```
</summary>

```json
[
  {
    "Id": "r-p74l",
    "Arn": "arn:aws:organizations::039444814027:root/o-p66trezrse/r-p74l",
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
    "Id": "039444814027",
    "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/039444814027",
    "Email": "iain+awsroot+zcskbx@isme.es",
    "Name": "isme-root-zcskbx",
    "Status": "ACTIVE",
    "JoinedMethod": "INVITED",
    "JoinedTimestamp": "2023-06-08T12:14:55.704000+02:00",
    "Type": "ACCOUNT",
    "Parent": "r-p74l"
  },
  {
    "Id": "ou-p74l-a2llanp8",
    "Arn": "arn:aws:organizations::039444814027:ou/o-p66trezrse/ou-p74l-a2llanp8",
    "Name": "Sandbox",
    "Type": "ORGANIZATIONAL_UNIT",
    "Parent": "r-p74l"
  },
  {
    "Id": "ou-p74l-094nw8v7",
    "Arn": "arn:aws:organizations::039444814027:ou/o-p66trezrse/ou-p74l-094nw8v7",
    "Name": "Security",
    "Type": "ORGANIZATIONAL_UNIT",
    "Parent": "r-p74l"
  },
  {
    "Id": "386884128156",
    "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/386884128156",
    "Email": "iain+awsroot+zcskbx+log-archive@isme.es",
    "Name": "Log Archive",
    "Status": "ACTIVE",
    "JoinedMethod": "CREATED",
    "JoinedTimestamp": "2023-06-08T12:15:24.407000+02:00",
    "Type": "ACCOUNT",
    "Parent": "ou-p74l-094nw8v7"
  },
  {
    "Id": "466721047587",
    "Arn": "arn:aws:organizations::039444814027:account/o-p66trezrse/466721047587",
    "Email": "iain+awsroot+zcskbx+audit@isme.es",
    "Name": "Audit",
    "Status": "ACTIVE",
    "JoinedMethod": "CREATED",
    "JoinedTimestamp": "2023-06-08T12:15:15.815000+02:00",
    "Type": "ACCOUNT",
    "Parent": "ou-p74l-094nw8v7"
  }
]
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
