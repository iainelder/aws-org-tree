# Building a hierarchy bridge table

In this example, we have two AWS organizations, org_A and org_B. We will build a hierarchical bridge table for each of these organizations.

See [What is a Hierarchical Bridge table](#what-is-a-hierarchical-bridge-table) below for a reminder of what it is and why it's useful.

# Procedure

A CLI profile for the management account of org_A and org_B is defined.

```bash
export AWS_PROFILE=org_A

aws-org-tree json-flat \
> org-tree_A.json

export AWS_PROFILE=org_B

aws-org-tree json-flat \
> org-tree_B.json
```

Quality checks. The number of objects should be the number of accounts plus the number of OUs. (In this example the numbers are just made up and they won't necessarily add up.)

```text
$ jq 'length' org-tree_cfs.json 
123
$ jq 'length' org-tree_dpp.json 
234
```

Covert to CSV and write to the database.

```bash
csvstack \
--groups A,B \
--group-name OrgScope \
<(cat org-tree_A.json | in2csv --format json) \
<(cat org-tree_B.json | in2csv --format json) \
| csvsql \
  --snifflimit 0 \
  --db sqlite:///report.db \
  --tables org_tree_dump \
  --overwrite \
  --insert
```

Sqlite write mode:

```bash
sqlite3 report.db
```

Create brige table for the account hierarchy.

```sql
CREATE TABLE bridge AS
WITH rec (
    org_scope,
    superior_key,
    subordinate_key,
    parent_key,
    level,
    top_flag
) AS (
  SELECT
    OrgScope AS org_scope,
    Id AS superior_key,
    Id AS subordinate_key,
    Parent AS parent_key,
    0 AS level,
    1 AS top_flag
  FROM org_tree_dump
  
  UNION ALL
  
  SELECT
    rec_plus1.OrgScope AS org_scope,
    rec.superior_key,
    rec_plus1.Id AS subordinate_key,
    rec_plus1.Parent AS parent_key,
    rec.level + 1 AS level,
    0 AS top_flag
  FROM rec
  INNER JOIN org_tree_dump AS rec_plus1 ON (rec.subordinate_key = rec_plus1.Parent)
)
SELECT *
FROM rec
ORDER BY org_scope, superior_key, level, subordinate_key;
```

Sqlite reporting mode:

```bash
sqlite3 --csv --header --readonly report.db
```

Check it was loaded correctly by counting the accounts in each OU.

```sql
SELECT
  ohyou.OrgScope,
  ohyou.Id,
  ohyou.Name,
  COUNT(*) AS accounts
FROM org_tree_dump AS ohyou
INNER JOIN bridge ON (ohyou.Id = bridge.superior_key)
INNER JOIN org_tree_dump AS sub ON (sub.Id = bridge.subordinate_key)
WHERE
  ohyou.Type = 'ORGANIZATIONAL_UNIT' AND
  bridge.top_flag = 0 AND
  sub.Type = 'ACCOUNT'
GROUP BY
  ohyou.OrgScope,
  ohyou.Id,
  ohyou.Name
ORDER BY ohyou.OrgScope, accounts DESC;
```

|OrgScope|Id              |Name               |accounts|
|--------|----------------|-------------------|--------|
|A       |ou-aaaa-00000000|Main               |249     |
|A       |ou-aaaa-11111111|Testing            |220     |
|A       |ou-aaaa-22222222|Suspended          |39      |
|A       |ou-aaaa-33333333|Prod               |28      |
|...     |...             |...                |...     |
|B       |ou-bbbb-00000000|Main               |458     |
|B       |ou-bbbb-11111111|Testing            |288     |
|B       |ou-bbbb-22222222|Prod               |170     |
|B       |ou-bbbb-33333333|Suspended          |57      |
|...     |...             |...                |...     |

# What is a hierarchical bridge table?

Introduction to hierarchical dimesions.

https://www.nuwavesolutions.com/simple-hierarchical-dimensions-html/

> Hierarchical dimensions are those dimensions which have a parent/child relationship. In simple hierarchies there every child has a parent at the level above with no skipping of levels. A date (day, month, quarter, year) is the most common example of a simple hierarchical dimension and one that is used by all dimensional data warehouses.

An AWS organization is a hierarchy, but it can skip levels.

So the AWS organization is a ragged hierarchy. See the solutions using recursion and the hierarchy bridge table.

https://www.nuwavesolutions.com/ragged_hierarchical_dimensions/

> Another way to work with a ragged hierarchy is to use a recursion to address the recursive hierarchy. Recursion is created when the child record has a relationship to the parent record as an attribute of the child record.

> This is the simplest and most flexible solution to address the challenge of a ragged hierarchy.

> To create a hierarchy bridge table you will create a table consisting of each record associated with itself and its association with all of its subordinates regardless of level. You should also capture the number of levels removed from itself and flags indicating if this is the top of the hierarchy or the bottom of the hierarchy.

A way to build a hierchy bridge table in SQL from a recursive table using a recursive CTE. 

http://www.kimballgroup.com/wp-content/uploads/2014/11/Building-the-Hierarchy-Bridge-Table.pdf

From Kimball:

> In our books and classes, we describe a powerful technique for representing complex ragged 
hierarchies of indeterminate depth. The centerpiece of the design is a bridge table whose grain is every path from any given node in the tree to all the descendants below that node. 
 
> Please see pages 215 to 224 in The Data Warehouse Toolkit, Third Edition, for an in-depth discussion of this approach to modeling ragged hierarchies.

Another example of building a hierarchical bridge table using Oracle syntax.

https://www.nuwavesolutions.com/loading-hierarchical-bridge-tables/

The query to build the hierarchy bridge table is adapted from the examples in the linked resources.
