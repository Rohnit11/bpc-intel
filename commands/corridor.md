# /corridor

Generate the K-beauty corridor brief (Korea → India).

Renders `corridor_brief.md.j2` from `config/corridor.yaml` + processed data:
corridor sizing ([CORRIDOR]-tagged), Korea→India trade flows (UN Comtrade),
conduit → brand map (Nykaa, Tira, Flipkart, Amazon, q-commerce), ranked
whitespace, and CDSCO import regulation.

Run: `python -m lib.reports.snapshot corridor`
