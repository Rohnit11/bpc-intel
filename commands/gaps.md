# /gaps

Show the current gaps register (missing segment × geography × metric cells).

Rebuilds from the taxonomy vs processed data and writes
`reports/latest/gaps_register.md`, with a suggested source per gap.

Run: `python -c "from lib.analysis.gaps import scan_gaps, format_gaps_register; from pathlib import Path; g=scan_gaps(); Path('reports/latest/gaps_register.md').write_text(format_gaps_register(g), encoding='utf-8'); print(len(g),'gaps')"`
