from pathlib import Path

STATIC = Path(__file__).parents[1] / "static"

def test_server_playback_is_split_prefetched_and_double_buffered():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert 'id="audio" preload="auto"' in html
    assert 'id="audioNext" preload="auto"' in html
    assert "TTS_PART_MAX=850" in js
    assert "PREFETCH_PARTS=5" in js
    assert "function speechParts(" in js
    assert "function prefetchWindow(" in js
    assert "async function prepareStandby(" in js
    assert "st.standbyKey===entry.key" in js

def test_visual_chunks_are_distinct_from_internal_tts_parts():
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "function chunks(s,max=2800)" in js
    assert "function speechParts(text,max=TTS_PART_MAX)" in js


def test_tts_never_splits_a_punctuated_sentence_but_bounds_unpunctuated_text():
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "const TTS_PART_MAX=850" in js
    assert 'const endsSentence=/[.!?…]+["»”’)]*$/.test(x);' in js
    assert "if(x.length>max&&!endsSentence)" in js
    assert "splitUnpunctuatedSpeech(x,max)" in js
    assert "for(let i=0;i<x.length;i+=max)" not in js
