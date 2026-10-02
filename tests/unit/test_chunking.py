from battery_advisor.rag.chunking import split_markdown

def test_heading_path_prefix():
    md = "# Guide\n\n## LiFePO4\nCharge above 0C.\n\n## Li-ion\nLighter."
    chunks = split_markdown(md)
    assert [c.heading for c in chunks] == ["Guide > LiFePO4", "Guide > Li-ion"]
    assert chunks[0].text.startswith("Guide > LiFePO4")

def test_long_section_is_split():
    md = "## A\n" + "\n\n".join(["x" * 500] * 5)
    chunks = split_markdown(md, max_chars=1200)
    assert len(chunks) > 1 and all(len(c.text) < 1500 for c in chunks)