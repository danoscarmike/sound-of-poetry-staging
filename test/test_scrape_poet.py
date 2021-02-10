from scripts.scrape_poet import scrape_poet


# test poet with all values present
def test_scrape_heaney():
    heaney = scrape_poet('seamus-heaney')
    assert(heaney['name'] == 'Seamus Heaney')
    assert(heaney['meta'] == '1939–2013')
    assert("Region:" in heaney['attrs'].keys())
    assert("Ireland & Northern Ireland" in heaney['attrs']['Region:'])


# test poet with no date of birth/death
def test_scrape_wang():
    wang = scrape_poet('yun-wang')
    assert(wang['name'] == 'Yun Wang')
    assert(wang['meta'] == '')
    assert("Region:" in wang['attrs'].keys())
    assert("Asia, East" in wang['attrs']['Region:'])


# test poet with no 'more about' section
def test_scrape_cole():
    cole = scrape_poet('kevin-l-cole')
    assert(cole['name'] == 'Kevin L. Cole')
    assert(cole['meta'] == '')
    assert(len(cole['attrs'].keys()) == 0)
