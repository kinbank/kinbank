Kinbank (Parabank & Varikin)
============================

This repository contains the merged data from [Varikin](https://github.com/SamPassmore/kinbank) and [Parabank](https://github.com/parabank/parabank-kinship-data)




To Generate a Combined CLDF dataset:
------------------------------------

The shell utility [make](https://www.gnu.org/software/make/) and the programming language [python (v3.6+)](https://www.python.org/) are required.

1. Install the python requirements:

The libraries needed for the python merge script are [cldfbench](https://pypi.org/project/cldfbench/0.2.0/) and [pylexibank](https://pypi.org/project/pylexibank/). These will be
installed into a virtual environment using this command:

```shell
make install
```

2. Clone and update the datasets:

```shell
make data
```

3. Merge the datasets:

```shell
make merge
```

4. Generate CLDF:

```shell
make cldf
```
