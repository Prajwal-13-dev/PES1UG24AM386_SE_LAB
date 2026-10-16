\# Static Code Analysis — Issues Report



\*\*File:\*\* `tower\_maintenance.py`



\*\*Original Pylint score:\*\* 5.14/10



\## Identified Issues



| Issue | Type | Line(s) | Description | Fix Approach |

|---|---|---:|---|---|

| SQL injection risk | Security — Medium | 11 | The SQL query is constructed using string formatting, allowing an input such as a site name to interfere with the query. | Replace string formatting with parameterized SQL queries using `?` placeholders. |

| Unsafe pickle usage | Security — Medium | 43 | The code uses `pickle.loads()` to deserialize data. Deserializing untrusted pickle data can execute malicious code, and serialization is unnecessary for copying these query results. | Return the database query results directly using `fetchall()` and remove the `pickle` import. |

| Overly broad exception handling | Code quality — Medium | 20 | Catching `Exception` can hide unexpected errors and make debugging difficult. | Catch the relevant `sqlite3.Error` exceptions and handle failures clearly. |

| Missing tower ID handling | Potential runtime bug | 35–36 | If the supplied tower ID does not exist, `fetchone()` returns `None`, and accessing `row\[0]` raises an error. | Check whether a row exists before accessing its fault count. |

| Hardcoded password | Security — Low | 6 | A password is stored directly in the source code. The constant is also unused by the current demonstration. | Remove the unused constant. If authentication is added later, use an appropriate secret-management mechanism. |

| Inconsistent function naming | Style | 10, 15, 34 | Function names such as `addTower`, `serviceTower`, and `riskLevel` do not follow Python's recommended `snake\_case` convention. | Rename them to `add\_tower`, `service\_tower`, and `risk\_level`, updating their calls. |

| Missing docstrings | Code quality | 1, 10, 15, 25, 34, 42, 46 | The module and functions lack descriptions of their purpose and behavior. | Add a module docstring and concise docstrings for each function. |

| Lines exceed the recommended length | Style | 5, 11, 18, 35, 43 | Several lines exceed Flake8's 79-character limit, and some also exceed Pylint's 100-character limit. | Split long SQL statements and expressions across multiple lines. |

| Missing whitespace around operator | Style | 50 | The assignment `total=len(snapshot())` lacks spaces around the assignment operator. | Change it to `total = len(snapshot())`. |

| Excess blank lines | Style | 25 | The file contains too many consecutive blank lines before a function definition. | Keep no more than two blank lines between top-level definitions. |

| Unnecessary `else` after `return` | Code quality | 36–39 | The `else` branch is unnecessary because the preceding branch already returns a value. | Remove `else` and return the normal risk level directly after the high-risk check. |

| Global variable usage | Code quality | 16 | `serviceTower()` modifies `service\_count` using the `global` statement, increasing dependence on shared state. | Refactor the counting logic to avoid modifying a module-level variable directly. |



\## Summary



The original analysis identified security risks, maintainability concerns, possible runtime errors, and style violations. The code will be updated to address these problems while preserving tower registration, servicing, overdue-site detection, risk assessment, and the demonstration output.

