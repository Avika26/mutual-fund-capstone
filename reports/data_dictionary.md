\# Data Dictionary — Bluestock MF Capstone



\## dim\_fund

| Column | Type | Description |

|---|---|---|

| amfi\_code | TEXT (PK) | Unique AMFI scheme code |

| fund\_house | TEXT | AMC name |

| scheme\_name | TEXT | Official scheme name |

| category | TEXT | Equity / Debt |

| sub\_category | TEXT | Large Cap / Small Cap / etc. |

| expense\_ratio\_pct | REAL | Annual expense ratio % |

| risk\_category | TEXT | SEBI risk level |



\## fact\_nav

| Column | Type | Description |

|---|---|---|

| amfi\_code | TEXT (FK) | References dim\_fund |

| date | TEXT | NAV date (daily, gap-filled) |

| nav | REAL | Net Asset Value in Rs. |



\## fact\_transactions

| Column | Type | Description |

|---|---|---|

| investor\_id | TEXT | Unique investor ID |

| amfi\_code | TEXT (FK) | Fund invested in |

| transaction\_type | TEXT | SIP / Lumpsum / Redemption |

| amount\_inr | INTEGER | Transaction amount |

| state, city, city\_tier | TEXT | Investor geography |



\## fact\_performance

| Column | Type | Description |

|---|---|---|

| amfi\_code | TEXT (FK) | Fund reference |

| sharpe\_ratio | REAL | Risk-adjusted return metric |

| max\_drawdown\_pct | REAL | Worst peak-to-trough decline |



\## fact\_aum

| Column | Type | Description |

|---|---|---|

| fund\_house | TEXT | AMC name |

| aum\_crore | INTEGER | Assets under management, Rs. crore |



\## Source

All data sourced from AMFI India, mfapi.in, and provided project CSVs.

